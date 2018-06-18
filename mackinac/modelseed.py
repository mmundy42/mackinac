from __future__ import absolute_import
from time import sleep
from operator import itemgetter
from warnings import warn
from os.path import join

from cobra import Model, Reaction, Metabolite

from .SeedClient import SeedClient, ServerError, ObjectNotFoundError, JobError, handle_server_error
from .workspace import get_workspace_object_meta, get_workspace_object_data, put_workspace_object
from .modelutil import create_cobra_model, convert_suffix, calculate_likelihoods, get_model_statistics, \
    convert_gapfill_solutions, convert_fba_solutions
from .genome import get_genome_summary
from .logger import LOGGER

# ModelSEED production service endpoint
modelseed_url = 'https://p3.theseed.org/services/ProbModelSEED'

# ModelSEED development service endpoint
dev_modelseed_url = 'http://p3c.theseed.org/dev1/services/ProbModelSEED'

# Client for running functions on ModelSEED web service
ms_client = SeedClient(modelseed_url, 'ProbModelSEED')

# Name of folder where ModelSEED models are stored
model_folder = 'modelseed'


def calculate_modelseed_likelihoods(model_id, search_program_path, search_db_path, fid_role_path, work_folder):
    """ Calculate reaction likelihoods for a ModelSEED model.

    Reaction likelihood calculation is done locally and results are stored in the
    model's folder in workspace. Caller must run download_data_files() function
    before running this function to prepare for local calculation of likelihoods.

    Parameters
    ----------
    model_id : str
        ID of model
    search_program_path : str
        Path to search program executable
    search_db_path : str
        Path to search database file
    fid_role_path : str
        Path to feature ID to role ID mapping file
    work_folder : str
        Path to folder for storing intermediate files

    Returns
    -------
    dict
        Dictionary keyed by reaction ID of calculated likelihoods and statistics

    """

    return calculate_likelihoods(_make_modelseed_model_reference(model_id), search_program_path, search_db_path,
                                 fid_role_path, work_folder)


def create_cobra_model_from_modelseed_model(model_id, id_type='modelseed', validate=False):
    """ Create a COBRA model from a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])
    validate : bool
        When True, check for common problems

    Returns
    -------
    cobra.core.Model
        Model object
    """

    return create_cobra_model(_make_modelseed_model_reference(model_id), id_type=id_type, validate=validate)


def create_universal_model(template_reference, id_type='modelseed'):
    """ Create a universal model from a ModelSEED template model.

        A template model has all of the reactions and metabolites that are available for
        inclusion in a model. There are different template models for different types
        of organisms (e.g. gram negative bacteria). Use an universal model as input to
        one of the gap fill functions.

    Parameters
    ----------
    template_reference : str
        Workspace reference to template model
    id_type : {'modelseed', 'bigg'}, optional
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])

    Returns
    -------
    cobra.core.Model
        Model object with all reactions for models of a type of organism
    """

    # Get the template model data from the workspace object.
    data = get_workspace_object_data(template_reference)

    # Create a dict to look up compounds.
    compound_index = dict()
    for index in range(len(data['compounds'])):
        key = '~/compounds/id/{0}'.format(data['compounds'][index]['id'])
        compound_index[key] = index

    # Create a new COBRApy Model object.
    model = Model(data['id'], name=data['name'])

    # Add template compartments to the universal model.
    LOGGER.info('Started adding %d compartments from template model', len(data['compartments']))
    for index in range(len(data['compartments'])):
        modelseed_compartment = data['compartments'][index]
        model.compartments[modelseed_compartment['id']] = modelseed_compartment['name']
    LOGGER.info('Finished adding %d compartments to model', len(model.compartments))

    # Create Metabolite objects for all of the compounds in the template model. Metabolite
    # data is split between the "compcompounds" (compounds in a compartment) and the
    # "compounds" lists.
    LOGGER.info('Started adding %d metabolites from template model', len(data['compcompounds']))
    all_metabolites = list()
    for compcompound in data['compcompounds']:
        compound = data['compounds'][compound_index[compcompound['templatecompound_ref']]]
        cobra_id = convert_suffix(compcompound['id'], id_type)
        metabolite = Metabolite(id=cobra_id,
                                formula=compound['formula'],
                                name=compound['name'],
                                charge=compcompound['charge'],
                                compartment=compcompound['templatecompartment_ref'].split('/')[-1])
        all_metabolites.append(metabolite)
    model.add_metabolites(all_metabolites)
    LOGGER.info('Finished adding %d metabolites to model', len(model.metabolites))

    # Create Reaction objects for all of the reactions in the template model.
    LOGGER.info('Started adding %d reactions from template model', len(data['reactions']))
    all_reactions = list()
    for template_reaction in data['reactions']:
        # Set upper and lower bounds based directionality. Switch reverse reactions to
        # forward reactions.
        reverse = 1.0
        if template_reaction['direction'] == '=':
            lower_bound = -1000.0
            upper_bound = 1000.0
        elif template_reaction['direction'] == '>':
            lower_bound = 0.0
            upper_bound = 1000.0
        elif template_reaction['direction'] == '<':
            lower_bound = 0.0
            upper_bound = 1000.0
            reverse = -1.0
        else:
            warn('Reaction direction {0} assumed to be reversible for reaction {1}'
                 .format(template_reaction['direction'], template_reaction['id']))
            lower_bound = -1000.0
            upper_bound = 1000.0

        # Create the Reaction object.
        reaction = Reaction(id=convert_suffix(template_reaction['id'], id_type),
                            name=template_reaction['name'],
                            lower_bound=lower_bound,
                            upper_bound=upper_bound)

        # Create dictionary of metabolites and add them to the reaction.
        metabolites = dict()
        for reagent in template_reaction['templateReactionReagents']:
            cobra_metabolite_id = convert_suffix(reagent['templatecompcompound_ref'].split('/')[-1], id_type)
            metabolite = model.metabolites.get_by_id(cobra_metabolite_id)
            metabolites[metabolite] = float(reagent['coefficient']) * reverse
        reaction.add_metabolites(metabolites)

        # Add a note with the ModelSEED reaction type (universal, spontaneous, conditional, or gapfilling).
        reaction.notes['type'] = template_reaction['type']
        all_reactions.append(reaction)

    # Finally, add all of the reactions to the model.
    model.add_reactions(all_reactions)
    LOGGER.info('Finished adding %d reactions to model', len(model.reactions))

    return model


def delete_modelseed_model(model_id):
    """ Delete a ModelSEED model from the workspace.

    Parameters
    ----------
    model_id : str
        ID of model
    """

    reference = _make_modelseed_model_reference(model_id)
    # error = None
    LOGGER.info('Started delete model using web service for "%s"', reference)
    try:
        ms_client.call('delete_model', {'model': reference})
    except ServerError as e:
        raise handle_server_error(e, [reference])
        # error = handle_server_error(e, [reference])
    LOGGER.info('Finished delete model using web service for "%s"', reference)

    # if error: raise error
    return


def gapfill_modelseed_model(model_id, media_reference=None, likelihood=False, comprehensive=False):
    """ Run gap fill on a ModelSEED model.

    The ModelSEED model is updated with the reactions identified by gap fill that
    make the model feasible.

    Parameters
    ----------
    model_id : str
        ID of model
    media_reference : str, optional
        Workspace reference to media to gap fill on (default is complete media)
    likelihood : bool, optional
        True to use likelihood-based gap fill
    comprehensive : bool, optional
        True to run a comprehensive gap fill

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    reference = _make_modelseed_model_reference(model_id)
    params = dict()
    params['model'] = reference
    params['integrate_solution'] = 1
    if media_reference is not None:
        get_workspace_object_meta(media_reference)  # Confirm media object exists
        params['media'] = media_reference
    # if likelihood:
    #     params['probanno'] = 1
    # else:
    #     params['probanno'] = 0
    # if comprehensive:  # @TODO switch this to alpha?
    #     params['comprehensive_gapfill'] = 1

    try:
        get_model_statistics(reference)  # Confirm model exists
        job_id = ms_client.call('GapfillModel', params)
        LOGGER.info('Started job %s to run gapfill model for "%s"', job_id, reference)
        _wait_for_job(job_id)
    except ServerError as e:
        references = [reference]
        if media_reference is not None:
            references.append(media_reference)
        raise handle_server_error(e, references)

    return get_modelseed_model_stats(model_id)


def get_modelseed_fba_solutions(model_id):
    """ Get the list of fba solutions available for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    list
        List of fba solution data structures
    """

    reference = _make_modelseed_model_reference(model_id)
    LOGGER.info('Started get list of fba solutions using web service for "%s"', reference)
    try:
        get_model_statistics(reference)  # Confirm model exists
        solutions = ms_client.call('list_fba_studies', {'model': reference})
    except ServerError as e:
        raise handle_server_error(e, [reference])
    LOGGER.info('Finished get list of fba solutions using web service for "%s", found %d solutions',
                reference, len(solutions))

    return convert_fba_solutions(solutions)


def get_modelseed_gapfill_solutions(model_id, id_type='modelseed'):
    """ Get the list of gap fill solutions for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])

    Returns
    -------
    list
        List of gap fill solution data structures
    """

    reference = _make_modelseed_model_reference(model_id)
    LOGGER.info('Started get gapfill solutions using web service for "%s"', reference)
    try:
        get_model_statistics(reference)  # Confirm model exists
        solutions = ms_client.call('list_gapfill_solutions', {'model': reference})
    except ServerError as e:
        raise handle_server_error(e, [reference])
    LOGGER.info('Finished get gapfill solutions using web service for "%s", found %d solutions',
                reference, len(solutions))

    return convert_gapfill_solutions(solutions, id_type)


def get_modelseed_model_data(model_id):
    """ Get the model data for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        Name of model

    Returns
    -------
    dict
        Dictionary of all model data
    """

    reference = _make_modelseed_model_reference(model_id)
    LOGGER.info('Started get model data using web service for "%s"', reference)
    try:
        return ms_client.call('get_model', {'model': reference, 'to': 1})
    except ServerError as e:
        raise handle_server_error(e, [reference])


def get_modelseed_model_stats(model_id):
    """ Get the model statistics for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    return get_model_statistics(_make_modelseed_model_reference(model_id))


def list_modelseed_models(sort_key='rundate', print_output=False):
    """ List the ModelSEED models for the user.

    Parameters
    ----------
    sort_key : {'rundate', 'id', 'name'}, optional
        Name of field to use as sort key for output
    print_output : bool, optional
        When True, print a summary of the list instead of returning the list

    Returns
    -------
    list or None
        List of model statistics dictionaries or None if printed output
    """

    LOGGER.info('Started list models using web service')
    try:
        output = ms_client.call('list_models', {})
    except ServerError as e:
        raise handle_server_error(e)
    LOGGER.info('Finished list models using web service')
    reverse = False
    if sort_key == 'rundate':
        reverse = True
    output.sort(key=itemgetter(sort_key), reverse=reverse)
    if not print_output:
        return output
    for model in output:
        if model['status'] == 'complete':
            print('Model {0} for organism {1} with {2} reactions and {3} metabolites'
                  .format(model['ref'], model['name'], model['num_reactions'], model['num_compounds']))
    return None


def optimize_modelseed_model(model_id, media_reference=None):
    """ Run flux balance analysis on a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    media_reference : str
        Workspace reference to media to optimize on (default is complete media)

    Returns
    -------
    float
        Objective value
    """

    # Get the current list of fba solutions which is the only way to tell if this
    # optimization is successful because fba_count is not updated in the metadata.
    # And it confirms that the model exists.
    fba_count = len(get_modelseed_fba_solutions(model_id))

    # Set input parameters for method.
    reference = _make_modelseed_model_reference(model_id)
    params = dict()
    params['model'] = reference
    params['predict_essentiality'] = 1
    if media_reference is not None:
        get_workspace_object_meta(media_reference)  # Confirm media object exists
        params['media'] = media_reference

    # Run the server method.
    try:
        job_id = ms_client.call('FluxBalanceAnalysis', params)
        LOGGER.info('Started job %s to run flux balance analysis for "%s"', job_id, reference)
        _wait_for_job(job_id)
    except ServerError as e:
        references = [reference]
        if media_reference is not None:
            references.append(media_reference)
        raise handle_server_error(e, references)

    # The completed job does not have the reference to the fba object that
    # was just created so get the list of solutions. Last completed
    # solution is first in the list.
    solutions = get_modelseed_fba_solutions(model_id)
    if fba_count == len(solutions):
        warn('Optimization for {0} did not return a solution'.format(model_id))
        return 0.0
    return float(solutions[0]['objective'])


def reconstruct_modelseed_model(genome_id, model_id, template_reference=None):
    """ Reconstruct a draft ModelSEED model for an organism.

    Parameters
    ----------
    genome_id : str
        Genome ID or workspace reference to genome
    model_id : str
        ID of output model
    template_reference : str, optional
        Workspace reference to template model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # Confirm genome ID is available in PATRIC.
    get_genome_summary(genome_id)

    # Set input parameters for method.
    params = dict()
    params['genome'] = 'PATRICSOLR:' + genome_id
    # params['fulldb'] = 0
    params['output_file'] = model_id
    if template_reference is not None:
        params['template_model'] = template_reference
    params['gapfill'] = 0
    params['predict_essentiality'] = 0

    # Workaround for ModelSEED workspace bug. The user's modelseed folder must exist before saving
    # the model. Otherwise the type of the folder created for the model is not "modelfolder" and
    # subsequent operations on the model will fail.
    if ms_client.username is None:
        ms_client.set_authentication_token()
    folder_reference = '/{0}/{1}'.format(ms_client.username, model_folder)
    try:
        get_workspace_object_meta(folder_reference)
    except ObjectNotFoundError:
        put_workspace_object(folder_reference, 'folder')
        LOGGER.info('Created modelseed folder in workspace for "%s"', ms_client.username)

    # Run the server method.
    try:
        job_id = ms_client.call('ModelReconstruction', params)
        LOGGER.info('Started job %s to run model reconstruction for "%s"', job_id, params['genome'])
        _wait_for_job(job_id)
    except ServerError as e:
        references = None
        if template_reference is not None:
            references = [template_reference]
        raise handle_server_error(e, references)

    # Get the model statistics for the model.
    stats = get_modelseed_model_stats(model_id)
    if stats['num_genes'] == 0:  # ModelSEED does not return an error if the genome ID is invalid
        warn('Model for genome ID {0} has no genes, verify genome ID is valid'.format(genome_id))
    return stats


def save_modelseed_template_model(template_reference, template_folder):
    """ Save a ModelSEED template model to source file format.

    Parameters
    ----------
    template_reference : str
        Workspace reference to template model
    template_folder : str
        Path to folder for storing files with template data
    """

    # Get the template model data from the workspace object.
    data = get_workspace_object_data(template_reference)

    # Convert roles to source file format and store in file.
    with open(join(template_folder, 'roles.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'name', 'source', 'features', 'aliases']) + '\n')
        data['roles'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['roles'])):
            item = data['roles'][index]
            features = 'null'
            if len(item['features']) > 0:
                features = ';'.join(item['features'])
            aliases = 'null'  # Aliases are not currently valid
            lines.append('\t'.join([item['id'], item['name'], item['source'], features, aliases]))
        handle.write('\n'.join(lines) + '\n')

    # Convert complexes to source file format and store in file.
    with open(join(template_folder, 'complexes.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'name', 'source', 'reference', 'confidence', 'roles']) + '\n')
        data['complexes'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['complexes'])):
            item = data['complexes'][index]
            complexrole = 'null'
            if len(item['complexroles']) > 0:
                # Note that second field can also be "involved" but that info is lost when
                # building a template model.
                complexrole = '|'.join([';'.join([r['templaterole_ref'].split('/')[-1], 'triggering',
                                                  str(r['optional']), str(r['triggering'])])
                                        for r in item['complexroles']])
            lines.append('\t'.join([item['id'], item['name'], item['source'], item['reference'],
                                    str(item['confidence']), complexrole]))
        handle.write('\n'.join(lines) + '\n')

    # Convert compartments to source file format and store in file.
    with open(join(template_folder, 'compartments.tsv'), 'w') as handle:
        handle.write('\t'.join(['index', 'id', 'name', 'hierarchy', 'pH', 'aliases']) + '\n')
        data['compartments'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['compartments'])):
            item = data['compartments'][index]
            aliases = 'null'
            if len(item['aliases']) > 0:
                aliases = ';'.join(item['aliases'])
            lines.append('\t'.join([item['index'], item['id'], item['name'], str(item['hierarchy']),
                                    str(item['pH']), aliases]))
        handle.write('\n'.join(lines) + '\n')

    # Convert reactions to source file format and store in file.
    with open(join(template_folder, 'reactions.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'compartment', 'direction', 'gfdir', 'type', 'base_cost',
                                'forward_cost', 'reverse_cost', 'complexes']) + '\n')
        data['reactions'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['reactions'])):
            item = data['reactions'][index]
            compartments = 'c|e'  # No way to recover order of compartments so hard-code the value
            complexes = 'null'
            if len(item['templatecomplex_refs']) > 0:
                complexes = '|'.join([ref.split('/')[-1] for ref in item['templatecomplex_refs']])
            lines.append('\t'.join([item['id'].split('_')[0], compartments, item['direction'],
                                    item['GapfillDirection'], item['type'], str(item['base_cost']),
                                    str(item['forward_penalty']), str(item['reverse_penalty']),
                                    complexes]))
        handle.write('\n'.join(lines) + '\n')

    # Convert biomasses to source file format and store in two files.
    with open(join(template_folder, 'biomasses.tsv'), 'w') as b_handle:
        with open(join(template_folder, 'biomass_metabolites.tsv'), 'w') as c_handle:
            b_handle.write('\t'.join(['id', 'name', 'type', 'other', 'dna', 'rna', 'protein', 'lipid',
                                      'cellwall', 'cofactor', 'energy']) + '\n')
            c_handle.write('\t'.join(['biomass_id', 'id', 'coefficient', 'coefficient_type', 'class',
                                      'linked_compounds', 'compartment']) + '\n')
            data['biomasses'].sort(key=itemgetter('id'))
            b_lines = list()
            c_lines = list()
            for b_index in range(len(data['biomasses'])):
                item = data['biomasses'][b_index]
                b_lines.append('\t'.join([item['id'], item['name'], item['type'], str(item['other']),
                                          str(item['dna']), str(item['rna']), str(item['protein']),
                                          str(item['lipid']), str(item['cellwall']), str(item['cofactor']),
                                          str(item['energy'])]))
                item['templateBiomassComponents'].sort(key=itemgetter('class'))
                for c_index in range(len(item['templateBiomassComponents'])):
                    c_item = item['templateBiomassComponents'][c_index]
                    parts = c_item['templatecompcompound_ref'].split('/')[-1].split('_')
                    parts[0] += '_0'  # Really should look up compartment ID in parts[1] and use index number
                    linked = 'null'
                    if len(c_item['linked_compound_refs']) > 0:
                        lc = list()
                        for l_index in range(len(c_item['linked_compound_refs'])):
                            lc.append(
                                ':'.join([c_item['linked_compound_refs'][l_index].split('/')[-1].split('_')[0] + '_0',
                                          str(c_item['link_coefficients'][l_index])]))
                        linked = '|'.join(lc)
                    c_lines.append('\t'.join([item['id'], parts[0], str(c_item['coefficient']),
                                              c_item['coefficient_type'], c_item['class'], linked, parts[1]]))
            b_handle.write('\n'.join(b_lines) + '\n')
            c_handle.write('\n'.join(c_lines) + '\n')

    return


def _make_modelseed_model_folder_reference():
    """ Make a workspace reference to user's ModelSEED model folder.

    Returns
    -------
    str
        Reference to user's model folder
    """

    if ms_client.username is None:
        ms_client.set_authentication_token()
    return '/{0}/{1}'.format(ms_client.username, model_folder)


def _make_modelseed_model_reference(model_id):
    """ Make a workspace reference to a model object.

    Parameters
    ----------
    model_id : str
        Name of object

    Returns
    -------
    str
        Reference to object in user's model folder
    """

    return '{0}/{1}'.format(_make_modelseed_model_folder_reference(), model_id)


def _wait_for_job(job_id):
    """ Wait for a job submitted to the ModelSEED app service to end.

    Parameters
    ----------
    job_id : str
        ID of submitted job

    Returns
    -------
    dict
        Task structure with status of job

    Raises
    ------
    JobError
        When a job with the specified ID was not found
    """

    LOGGER.info('Started to wait for job %s', job_id)
    task = None
    done = False
    while not done:
        jobs = ms_client.call('CheckJobs', {})
        if job_id in jobs:
            task = jobs[job_id]
            if task['status'] == 'failed':
                if 'error' in task:
                    raise ServerError(task['error'])
                raise ServerError('Job submitted to ModelSEED app service failed, no details provided in response')
            elif task['status'] == 'completed':
                LOGGER.info('Job %s completed successfully', job_id)
                done = True
            else:
                sleep(3)
        else:
            raise JobError('Job {0} was not found'.format(job_id))
    return task

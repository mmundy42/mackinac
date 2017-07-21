
Working with your ModelSEED workspace
-------------------------------------

Mackinac provides functions for managing and working with your ModelSEED
workspace.

.. code:: ipython2

    import mackinac

Get a list of objects in a folder in a ModelSEED workspace with
``list_workspace_objects()``. For example, get a list of all of the
media available for gap filling with this command:

.. code:: ipython2

    mackinac.list_workspace_objects('/chenry/public/modelsupport/media', print_output=True)


.. parsed-literal::

    Contents of /chenry/public/modelsupport/media:
    -rr chenry    	       605	2015-05-11T05:39:01	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-D-galactosamine
    -rr chenry    	       590	2015-05-11T05:39:01	media       	/chenry/public/modelsupport/media/Sulfate-L-Arabitol
    -rr chenry    	       584	2015-05-11T05:39:01	media       	/chenry/public/modelsupport/media/Carbon-tricarballylate
    -rr chenry    	       584	2015-05-11T05:39:01	media       	/chenry/public/modelsupport/media/Sulfate-Cystathionine
    -rr chenry    	       590	2015-05-11T05:39:01	media       	/chenry/public/modelsupport/media/Sulfate-Thymidine
    -rr chenry    	       582	2015-05-11T05:39:02	media       	/chenry/public/modelsupport/media/Phosphate-O-Phospho-L-Serine
    -rr chenry    	       583	2015-05-11T05:39:02	media       	/chenry/public/modelsupport/media/Sulfate-L-Methionine
    -rr chenry    	       590	2015-05-11T05:39:02	media       	/chenry/public/modelsupport/media/Sulfate-D-Galactose
    -rr chenry    	       587	2015-05-11T05:39:02	media       	/chenry/public/modelsupport/media/Phosphate-Adenosine-2-3-Cyclic-Monophosphate
    -rr chenry    	       591	2015-05-11T05:39:02	media       	/chenry/public/modelsupport/media/Sulfate-Xanthosine
    -rr chenry    	       588	2015-05-11T05:39:03	media       	/chenry/public/modelsupport/media/Sulfate-Uridine
    -rr chenry    	       590	2015-05-11T05:39:03	media       	/chenry/public/modelsupport/media/Sulfate-D-Psicose
    -rr chenry    	       586	2015-05-11T05:39:03	media       	/chenry/public/modelsupport/media/Phosphate-Cytidine-2-Monophosphate
    -rr chenry    	       587	2015-05-11T05:39:04	media       	/chenry/public/modelsupport/media/Nitrogen-L-Pyroglutamic-Acid
    -rr chenry    	       579	2015-05-11T05:39:04	media       	/chenry/public/modelsupport/media/Carbon-L-Rhamnose
    -rr chenry    	       589	2015-05-11T05:39:04	media       	/chenry/public/modelsupport/media/Sulfate-L-Lysine
    -rr chenry    	       580	2015-05-11T05:39:04	media       	/chenry/public/modelsupport/media/Nitrogen-Uric-Acid
    -rr chenry    	       590	2015-05-11T05:39:04	media       	/chenry/public/modelsupport/media/Sulfate-D-Arabitol
    -rr chenry    	       597	2015-05-11T05:39:05	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-met-l
    -rr chenry    	       592	2015-05-11T05:39:05	media       	/chenry/public/modelsupport/media/Sulfate-D-Glucuronate
    -rr chenry    	       577	2015-05-11T05:39:05	media       	/chenry/public/modelsupport/media/Carbon-L-Malic-Acid
    -rr chenry    	       578	2015-05-11T05:39:05	media       	/chenry/public/modelsupport/media/Carbon-D-Psicose
    -rr chenry    	       582	2015-05-11T05:39:05	media       	/chenry/public/modelsupport/media/Nitrogen-Nitrite
    -rr chenry    	       589	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Carbon-N-Acetyl-L-Glutamic-Acid
    -rr chenry    	       578	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Nitrogen-Xanthine
    -rr chenry    	       589	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Sulfate-Tyramine
    -rr chenry    	       585	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Carbon-b-Phenylethylamine
    -rr chenry    	       578	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Carbon-L-Alanine
    -rr chenry    	       583	2015-05-11T05:39:06	media       	/chenry/public/modelsupport/media/Nitrogen-Tyramine
    -rr chenry    	       578	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Phosphate-Phosphate
    -rr chenry    	       587	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Nitrogen-Ethanolamine
    -rr chenry    	       581	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Carbon-Mucic-Acid
    -rr chenry    	       588	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Sulfate-Citrate
    -rr chenry    	       591	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Carbon-N-Acetyl-D-Glucosamine
    -rr chenry    	       592	2015-05-11T05:39:07	media       	/chenry/public/modelsupport/media/Sulfate-L-Glutamate
    -rr chenry    	       596	2015-05-11T05:39:08	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-glu-l
    -rr chenry    	       592	2015-05-11T05:39:08	media       	/chenry/public/modelsupport/media/Sulfate-Maltotriose
    -rr chenry    	       590	2015-05-11T05:39:10	media       	/chenry/public/modelsupport/media/Sulfate-1H-Imidazole-4-ethanamin
    -rr chenry    	       590	2015-05-11T05:39:10	media       	/chenry/public/modelsupport/media/Sulfate-Glycerone
    -rr chenry    	       586	2015-05-11T05:39:10	media       	/chenry/public/modelsupport/media/Nitrogen-L-Glutamine
    -rr chenry    	       591	2015-05-11T05:39:10	media       	/chenry/public/modelsupport/media/Nitrogen-b-Phenylethylamine
    -rr chenry    	       581	2015-05-11T05:39:10	media       	/chenry/public/modelsupport/media/Sulfate-Cysteamine
    -rr chenry    	       574	2015-05-11T05:39:11	media       	/chenry/public/modelsupport/media/Sulfate-Glutathione
    -rr chenry    	       596	2015-05-11T05:39:11	media       	/chenry/public/modelsupport/media/Sulfate-D-Galactosamine
    -rr chenry    	       582	2015-05-11T05:39:11	media       	/chenry/public/modelsupport/media/Sulfate-D-L-Lipoamide
    -rr chenry    	       584	2015-05-11T05:39:11	media       	/chenry/public/modelsupport/media/Carbon-Butylamine-sec
    -rr chenry    	       589	2015-05-11T05:39:11	media       	/chenry/public/modelsupport/media/Sulfate-6-Deoxy-D-galactose
    -rr chenry    	      1437	2015-05-11T05:39:12	media       	/chenry/public/modelsupport/media/NMS
    -rr chenry    	       597	2015-05-11T05:39:12	media       	/chenry/public/modelsupport/media/Nitrogen-N-Acetyl-D-L-Glutamic-Acid
    -rr chenry    	       589	2015-05-11T05:39:13	media       	/chenry/public/modelsupport/media/Sulfate-6-Deoxy-L-galactose
    -rr chenry    	       589	2015-05-11T05:39:13	media       	/chenry/public/modelsupport/media/Sulfate-Tween-20
    -rr chenry    	       579	2015-05-11T05:39:13	media       	/chenry/public/modelsupport/media/Nitrogen-D-Glucosamine
    -rr chenry    	       573	2015-05-11T05:39:13	media       	/chenry/public/modelsupport/media/Carbon-D-Gluconic-Acid
    -rr chenry    	       591	2015-05-11T05:39:14	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-D-L-Methionine
    -rr chenry    	       597	2015-05-11T05:39:14	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-ile-l
    -rr chenry    	       588	2015-05-11T05:39:14	media       	/chenry/public/modelsupport/media/Sulfate-Ribitol
    -rr chenry    	       582	2015-05-11T05:39:14	media       	/chenry/public/modelsupport/media/Nitrogen-Uridine
    -rr chenry    	       591	2015-05-11T05:39:14	media       	/chenry/public/modelsupport/media/Sulfate-D-Fructose
    -rr chenry    	       584	2015-05-11T05:39:15	media       	/chenry/public/modelsupport/media/Nitrogen-L-Proline
    -rr chenry    	       580	2015-05-11T05:39:15	media       	/chenry/public/modelsupport/media/Carbon-L-Aspartic-Acid
    -rr chenry    	       590	2015-05-11T05:39:15	media       	/chenry/public/modelsupport/media/Sulfate-L-Alanine
    -rr chenry    	       582	2015-05-11T05:39:16	media       	/chenry/public/modelsupport/media/Nitrogen-Glycine
    -rr chenry    	       580	2015-05-11T05:39:16	media       	/chenry/public/modelsupport/media/Carbon-L-Glutamic-Acid
    -rr chenry    	       588	2015-05-11T05:39:17	media       	/chenry/public/modelsupport/media/Sulfate-Dextrin
    -rr chenry    	       590	2015-05-11T05:39:17	media       	/chenry/public/modelsupport/media/Sulfate-L-Cystine
    -rr chenry    	       582	2015-05-11T05:39:18	media       	/chenry/public/modelsupport/media/Nitrogen-Nitrate
    -rr chenry    	       211	2015-05-11T05:39:18	media       	/chenry/public/modelsupport/media/MinimalGrowthNoMedia
    -rr chenry    	      2121	2015-05-11T05:39:18	media       	/chenry/public/modelsupport/media/ArgonneLBMedia
    -rr chenry    	       590	2015-05-11T05:39:18	media       	/chenry/public/modelsupport/media/Nitrogen-D-Galactosamine
    -rr chenry    	       582	2015-05-11T05:39:18	media       	/chenry/public/modelsupport/media/Biolog-C-dna
    -rr chenry    	       579	2015-05-11T05:39:19	media       	/chenry/public/modelsupport/media/Carbon-b-D-Allose
    -rr chenry    	       588	2015-05-11T05:39:19	media       	/chenry/public/modelsupport/media/Sulfate-Sucrose
    -rr chenry    	       583	2015-05-11T05:39:19	media       	/chenry/public/modelsupport/media/Nitrogen-L-Lysine
    -rr chenry    	       582	2015-05-11T05:39:19	media       	/chenry/public/modelsupport/media/Nitrogen-Gly-Gln
    -rr chenry    	       588	2015-05-11T05:39:19	media       	/chenry/public/modelsupport/media/Sulfate-Ala-His
    -rr chenry    	       581	2015-05-11T05:39:20	media       	/chenry/public/modelsupport/media/Carbon-L-Asparagine
    -rr chenry    	       586	2015-05-11T05:39:21	media       	/chenry/public/modelsupport/media/Nitrogen-L-Glutamic-Acid
    -rr chenry    	       590	2015-05-11T05:39:21	media       	/chenry/public/modelsupport/media/Phosphate-D-2-Phospho-Glyceric-Acid
    -rr chenry    	       575	2015-05-11T05:39:21	media       	/chenry/public/modelsupport/media/Carbon-Mannan
    -rr chenry    	       592	2015-05-11T05:39:21	media       	/chenry/public/modelsupport/media/Sulfate-L-Arabinose
    -rr chenry    	       577	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Carbon-Tyramine
    -rr chenry    	       592	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Sulfate-Gentiobiose
    -rr chenry    	       556	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Sulfate-NH3
    -rr chenry    	       588	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Sulfate-Galactitol
    -rr chenry    	        38	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Complete
    -rr chenry    	       587	2015-05-11T05:39:22	media       	/chenry/public/modelsupport/media/Nitrogen-L-Asparagine
    -rr chenry    	       587	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Sulfate-Biuret
    -rr chenry    	       577	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Carbon-D-Malic-Acid
    -rr chenry    	       576	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Carbon-Sucrose
    -rr chenry    	       576	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Carbon-Maltose
    -rr chenry    	       578	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Sulfate-Taurine
    -rr chenry    	       592	2015-05-11T05:39:23	media       	/chenry/public/modelsupport/media/Sulfate-L-Histidine
    -rr chenry    	       590	2015-05-11T05:39:24	media       	/chenry/public/modelsupport/media/Sulfate-D-Alanine
    -rr chenry    	       583	2015-05-11T05:39:25	media       	/chenry/public/modelsupport/media/Sulfate-D-Methionine
    -rr chenry    	       586	2015-05-11T05:39:25	media       	/chenry/public/modelsupport/media/Sulfate-Arbutin
    -rr chenry    	       586	2015-05-11T05:39:25	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Asp
    -rr chenry    	       585	2015-05-11T05:39:25	media       	/chenry/public/modelsupport/media/Nitrogen-L-Tyrosine
    -rr chenry    	       593	2015-05-11T05:39:25	media       	/chenry/public/modelsupport/media/Carbon-N-Acetyl-D-Galactosamine
    -rr chenry    	       586	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Carbon-d-Amino-Valeric-Acid
    -rr chenry    	       593	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Sulfate-L-Isoleucine
    -rr chenry    	       589	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Sulfate-R-R-Tartaric-Acid
    -rr chenry    	       587	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Sulfate-Uracil
    -rr chenry    	       596	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Sulfate-Propane-1-2-diol
    -rr chenry    	       589	2015-05-11T05:39:26	media       	/chenry/public/modelsupport/media/Sulfate-L-Valine
    -rr chenry    	       607	2015-05-11T05:39:27	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-acgam
    -rr chenry    	       581	2015-05-11T05:39:27	media       	/chenry/public/modelsupport/media/Carbon-D-Melezitose
    -rr chenry    	       589	2015-05-11T05:39:27	media       	/chenry/public/modelsupport/media/Sulfate-D-Ribose
    -rr chenry    	       577	2015-05-11T05:39:27	media       	/chenry/public/modelsupport/media/Carbon-D-Ribose
    -rr chenry    	       582	2015-05-11T05:39:27	media       	/chenry/public/modelsupport/media/Nitrogen-Inosine
    -rr chenry    	       576	2015-05-11T05:39:28	media       	/chenry/public/modelsupport/media/Carbon-Citric-Acid
    -rr chenry    	       581	2015-05-11T05:39:29	media       	/chenry/public/modelsupport/media/Phosphate-Tripolyphosphate
    -rr chenry    	       587	2015-05-11T05:39:29	media       	/chenry/public/modelsupport/media/Nitrogen-L-Methionine
    -rr chenry    	       593	2015-05-11T05:39:29	media       	/chenry/public/modelsupport/media/Sulfate-D-Asparagine
    -rr chenry    	       589	2015-05-11T05:39:29	media       	/chenry/public/modelsupport/media/Carbon-D-Lactitol
    -rr chenry    	       591	2015-05-11T05:39:29	media       	/chenry/public/modelsupport/media/Sulfate-L-Rhamnose
    -rr chenry    	       574	2015-05-11T05:39:30	media       	/chenry/public/modelsupport/media/Carbon-2-3-Butanone
    -rr chenry    	       582	2015-05-11T05:39:30	media       	/chenry/public/modelsupport/media/Sulfate-2-Hydroxyethane-Sulfonic-Acid
    -rr chenry    	       588	2015-05-11T05:39:30	media       	/chenry/public/modelsupport/media/Sulfate-Xylitol
    -rr chenry    	       591	2015-05-11T05:39:30	media       	/chenry/public/modelsupport/media/Carbon-D-Fructose-6-Phosphate
    -rr chenry    	       584	2015-05-11T05:39:30	media       	/chenry/public/modelsupport/media/Carbon-L-Alanyl-Glycine
    -rr chenry    	       590	2015-05-11T05:39:31	media       	/chenry/public/modelsupport/media/Sulfate-Amygdalin
    -rr chenry    	       590	2015-05-11T05:39:31	media       	/chenry/public/modelsupport/media/Phosphate-D-Mannose-6-Phosphate
    -rr chenry    	       584	2015-05-11T05:39:31	media       	/chenry/public/modelsupport/media/Nitrogen-Histamine
    -rr chenry    	       578	2015-05-11T05:39:31	media       	/chenry/public/modelsupport/media/Carbon-Glycyl-L-Proline
    -rr chenry    	       594	2015-05-11T05:39:31	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-adn
    -rr chenry    	       576	2015-05-11T05:39:32	media       	/chenry/public/modelsupport/media/Carbon-Quinic-Acid
    -rr chenry    	       590	2015-05-11T05:39:33	media       	/chenry/public/modelsupport/media/Sulfate-Guanosine
    -rr chenry    	       596	2015-05-11T05:39:34	media       	/chenry/public/modelsupport/media/Sulfate-tricarballylate
    -rr chenry    	       588	2015-05-11T05:39:34	media       	/chenry/public/modelsupport/media/Carbon-D-Glucose-1-Phosphate
    -rr chenry    	       576	2015-05-11T05:39:34	media       	/chenry/public/modelsupport/media/Carbon-Salicin
    -rr chenry    	       576	2015-05-11T05:39:34	media       	/chenry/public/modelsupport/media/Carbon-Acetic-Acid
    -rr chenry    	       578	2015-05-11T05:39:34	media       	/chenry/public/modelsupport/media/Carbon-D-Mannose
    -rr chenry    	       590	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Sulfate-Acetamide
    -rr chenry    	       582	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Sulfate-Lanthionine
    -rr chenry    	       575	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Phosphate-Cytidine-3-Monophosphate
    -rr chenry    	       591	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Biolog-C-lac-S-cys-l
    -rr chenry    	       584	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Carbon-m-Tartaric-Acid
    -rr chenry    	       576	2015-05-11T05:39:35	media       	/chenry/public/modelsupport/media/Carbon-sorbate
    -rr chenry    	       554	2015-05-11T05:39:37	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-dna-P-dna
    -rr chenry    	       586	2015-05-11T05:39:37	media       	/chenry/public/modelsupport/media/Phosphate-O-Phospho-D-Tyrosine
    -rr chenry    	       585	2015-05-11T05:39:37	media       	/chenry/public/modelsupport/media/Nitrogen-Ethylamine
    -rr chenry    	       588	2015-05-11T05:39:37	media       	/chenry/public/modelsupport/media/Sulfate-Quinate
    -rr chenry    	       603	2015-05-11T05:39:37	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-D-glucosamine
    -rr chenry    	       590	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Sulfate-Stachyose
    -rr chenry    	       595	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Carbon-a-Methyl-D-Glucoside
    -rr chenry    	       578	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Phosphate-2-Aminoethyl-Phosphonic-Acid
    -rr chenry    	       591	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Sulfate-Galactarate
    -rr chenry    	       581	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Carbon-L-Pyroglutamic-Acid
    -rr chenry    	       583	2015-05-11T05:39:38	media       	/chenry/public/modelsupport/media/Nitrogen-Cytidine
    -rr chenry    	       590	2015-05-11T05:39:39	media       	/chenry/public/modelsupport/media/Sulfate-L-Proline
    -rr chenry    	       586	2015-05-11T05:39:39	media       	/chenry/public/modelsupport/media/Sulfate-p-Amino-Benzene-Sulfonic-Acid
    -rr chenry    	       576	2015-05-11T05:39:39	media       	/chenry/public/modelsupport/media/Carbon-Oxalic-Acid
    -rr chenry    	       589	2015-05-11T05:39:39	media       	/chenry/public/modelsupport/media/Phosphate-b-Glycerol-Phosphate
    -rr chenry    	       589	2015-05-11T05:39:39	media       	/chenry/public/modelsupport/media/Sulfate-Glycerol
    -rr chenry    	       577	2015-05-11T05:39:40	media       	/chenry/public/modelsupport/media/Carbon-Tween-80
    -rr chenry    	       579	2015-05-11T05:39:41	media       	/chenry/public/modelsupport/media/Carbon-D-Mannitol
    -rr chenry    	       588	2015-05-11T05:39:41	media       	/chenry/public/modelsupport/media/Sulfate-Ala-Gln
    -rr chenry    	       586	2015-05-11T05:39:41	media       	/chenry/public/modelsupport/media/Nitrogen-L-Aspartic-Acid
    -rr chenry    	       588	2015-05-11T05:39:41	media       	/chenry/public/modelsupport/media/Sulfate-Acetate
    -rr chenry    	       788	2015-05-11T05:39:41	media       	/chenry/public/modelsupport/media/7H9
    -rr chenry    	       586	2015-05-11T05:39:42	media       	/chenry/public/modelsupport/media/Phosphate-O-Phospho-D-Serine
    -rr chenry    	       578	2015-05-11T05:39:42	media       	/chenry/public/modelsupport/media/Carbon-D-L-Carnitine
    -rr chenry    	       592	2015-05-11T05:39:42	media       	/chenry/public/modelsupport/media/Phosphate-O-Phospho-L-Threonine
    -rr chenry    	       587	2015-05-11T05:39:42	media       	/chenry/public/modelsupport/media/Sulfate-D-Xylose
    -rr chenry    	       580	2015-05-11T05:39:42	media       	/chenry/public/modelsupport/media/Carbon-D-Saccharic-Acid
    -rr chenry    	       573	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Carbon-D-Glucosamine
    -rr chenry    	       589	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Sulfate-Cytosine
    -rr chenry    	       578	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Carbon-D-Arabitol
    -rr chenry    	       580	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Carbon-L-Threonine
    -rr chenry    	       588	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Sulfate-Maltose
    -rr chenry    	       587	2015-05-11T05:39:43	media       	/chenry/public/modelsupport/media/Carbon-g-Hydroxy-Butyric-Acid
    -rr chenry    	       587	2015-05-11T05:39:44	media       	/chenry/public/modelsupport/media/Phosphate-D-3-Phospho-Glyceric-Acid
    -rr chenry    	       591	2015-05-11T05:39:44	media       	/chenry/public/modelsupport/media/Carbon-N-Acetyl-b-D-Mannosamine
    -rr chenry    	       577	2015-05-11T05:39:45	media       	/chenry/public/modelsupport/media/Carbon-D-Fucose
    -rr chenry    	       588	2015-05-11T05:39:45	media       	/chenry/public/modelsupport/media/Sulfate-Adenine
    -rr chenry    	       591	2015-05-11T05:39:45	media       	/chenry/public/modelsupport/media/Phosphate-Uridine-2-Monophosphate
    -rr chenry    	      1333	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/MinimalGrowthNMS
    -rr chenry    	       596	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-his-l
    -rr chenry    	       596	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/Sulfate-L-alanylglycine
    -rr chenry    	       593	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/Carbon-p-Hydroxy-Phenylacetic-Acid
    -rr chenry    	       580	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/Carbon-L-Glutamine
    -rr chenry    	       578	2015-05-11T05:39:46	media       	/chenry/public/modelsupport/media/Carbon-D-Melibiose
    -rr chenry    	       576	2015-05-11T05:39:47	media       	/chenry/public/modelsupport/media/Carbon-Uridine
    -rr chenry    	       581	2015-05-11T05:39:47	media       	/chenry/public/modelsupport/media/Carbon-D-L-Octopamine
    -rr chenry    	       590	2015-05-11T05:39:48	media       	/chenry/public/modelsupport/media/Sulfate-L-Ornithine
    -rr chenry    	       598	2015-05-11T05:39:48	media       	/chenry/public/modelsupport/media/Sulfate-4-Hydroxybenzoate
    -rr chenry    	       560	2015-05-11T05:39:49	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-gly
    -rr chenry    	       586	2015-05-11T05:39:49	media       	/chenry/public/modelsupport/media/Nitrogen-D-Glutamic-Acid
    -rr chenry    	       580	2015-05-11T05:39:49	media       	/chenry/public/modelsupport/media/Carbon-Capric-Acid
    -rr chenry    	       589	2015-05-11T05:39:49	media       	/chenry/public/modelsupport/media/Sulfate-Butanoic-Acid
    -rr chenry    	       578	2015-05-11T05:39:49	media       	/chenry/public/modelsupport/media/Carbon-Glycyl-L-Glutamic-Acid
    -rr chenry    	       589	2015-05-11T05:39:50	media       	/chenry/public/modelsupport/media/Sulfate-D-Sorbitol
    -rr chenry    	       590	2015-05-11T05:39:50	media       	/chenry/public/modelsupport/media/Sulfate-Deoxyribose
    -rr chenry    	       597	2015-05-11T05:39:50	media       	/chenry/public/modelsupport/media/Nitrogen-D-L-a-Amino-N-Butyric-Acid
    -rr chenry    	      2134	2015-05-11T05:39:50	media       	/chenry/public/modelsupport/media/LB
    -rr chenry    	       559	2015-05-11T05:39:50	media       	/chenry/public/modelsupport/media/Biolog-C-ser-l-N-ser-l
    -rr chenry    	       577	2015-05-11T05:39:51	media       	/chenry/public/modelsupport/media/Phosphate-Phosphono-Acetic-Acid
    -rr chenry    	       578	2015-05-11T05:39:51	media       	/chenry/public/modelsupport/media/Carbon-Thymidine
    -rr chenry    	       573	2015-05-11T05:39:51	media       	/chenry/public/modelsupport/media/Carbon-2-3-Butanediol
    -rr chenry    	       577	2015-05-11T05:39:51	media       	/chenry/public/modelsupport/media/Carbon-Glycogen
    -rr chenry    	       588	2015-05-11T05:39:51	media       	/chenry/public/modelsupport/media/Sulfate-Gelatine
    -rr chenry    	       592	2015-05-11T05:39:52	media       	/chenry/public/modelsupport/media/Sulfate-D-Glucarate
    -rr chenry    	       578	2015-05-11T05:39:53	media       	/chenry/public/modelsupport/media/Sulfate-L-Cysteinyl-Glycine
    -rr chenry    	       594	2015-05-11T05:39:53	media       	/chenry/public/modelsupport/media/Sulfate-D-Mannosamine
    -rr chenry    	       584	2015-05-11T05:39:53	media       	/chenry/public/modelsupport/media/Nitrogen-Acetamide
    -rr chenry    	       600	2015-05-11T05:39:53	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-phe-l
    -rr chenry    	       589	2015-05-11T05:39:54	media       	/chenry/public/modelsupport/media/Carbon-b-Methyl-D-Glucoside
    -rr chenry    	       562	2015-05-11T05:39:54	media       	/chenry/public/modelsupport/media/Biolog-C-gln-l-N-gln-l
    -rr chenry    	       596	2015-05-11T05:39:54	media       	/chenry/public/modelsupport/media/Carbon-4-Hydroxy-L-Proline-trans
    -rr chenry    	       576	2015-05-11T05:39:54	media       	/chenry/public/modelsupport/media/Carbon-Xylitol
    -rr chenry    	       586	2015-05-11T05:39:55	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Glu
    -rr chenry    	       597	2015-05-11T05:39:55	media       	/chenry/public/modelsupport/media/Nitrogen-N-Acetyl-D-Mannosamine
    -rr chenry    	       586	2015-05-11T05:39:56	media       	/chenry/public/modelsupport/media/Nitrogen-D-Aspartic-Acid
    -rr chenry    	       591	2015-05-11T05:39:57	media       	/chenry/public/modelsupport/media/Sulfate-Putrescine
    -rr chenry    	       572	2015-05-11T05:39:58	media       	/chenry/public/modelsupport/media/Phosphate-Pyrophosphate
    -rr chenry    	       573	2015-05-11T05:39:58	media       	/chenry/public/modelsupport/media/Phosphate-Guanosine-3-5-Cyclic-Monophosphate
    -rr chenry    	       581	2015-05-11T05:39:58	media       	/chenry/public/modelsupport/media/Sulfate-L-Cysteic-Acid
    -rr chenry    	       588	2015-05-11T05:39:59	media       	/chenry/public/modelsupport/media/Sulfate-Nitrite
    -rr chenry    	       584	2015-05-11T05:39:59	media       	/chenry/public/modelsupport/media/Nitrogen-Adenosine
    -rr chenry    	       580	2015-05-11T05:39:59	media       	/chenry/public/modelsupport/media/Carbon-Citraconic-Acid
    -rr chenry    	       581	2015-05-11T05:39:59	media       	/chenry/public/modelsupport/media/Nitrogen-Biuret
    -rr chenry    	       576	2015-05-11T05:40:01	media       	/chenry/public/modelsupport/media/Carbon-Dextrin
    -rr chenry    	       590	2015-05-11T05:40:02	media       	/chenry/public/modelsupport/media/Sulfate-D-Mannose
    -rr chenry    	       592	2015-05-11T05:40:03	media       	/chenry/public/modelsupport/media/Sulfate-L-Glutamine
    -rr chenry    	       583	2015-05-11T05:40:03	media       	/chenry/public/modelsupport/media/Nitrogen-L-Valine
    -rr chenry    	       581	2015-05-11T05:40:03	media       	/chenry/public/modelsupport/media/Nitrogen-Uracil
    -rr chenry    	       584	2015-05-11T05:40:04	media       	/chenry/public/modelsupport/media/Nitrogen-Gly-Glu
    -rr chenry    	       582	2015-05-11T05:40:05	media       	/chenry/public/modelsupport/media/Carbon-D-Glucosaminic-Acid
    -rr chenry    	       578	2015-05-11T05:40:06	media       	/chenry/public/modelsupport/media/Sulfate-Sulfate
    -rr chenry    	       582	2015-05-11T05:40:07	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-His
    -rr chenry    	       584	2015-05-11T05:40:07	media       	/chenry/public/modelsupport/media/Nitrogen-Gly-Asn
    -rr chenry    	       584	2015-05-11T05:40:07	media       	/chenry/public/modelsupport/media/Sulfate-Tetrathionate
    -rr chenry    	       584	2015-05-11T05:40:14	media       	/chenry/public/modelsupport/media/Nitrogen-Formamide
    -rr chenry    	       583	2015-05-11T05:40:14	media       	/chenry/public/modelsupport/media/Carbon-a-Keto-Glutaric-Acid
    -rr chenry    	       584	2015-05-11T05:40:15	media       	/chenry/public/modelsupport/media/Nitrogen-Allantoin
    -rr chenry    	       585	2015-05-11T05:40:15	media       	/chenry/public/modelsupport/media/Sulfate-Acetoin
    -rr chenry    	       578	2015-05-11T05:40:22	media       	/chenry/public/modelsupport/media/Carbon-L-Proline
    -rr chenry    	       587	2015-05-11T05:40:22	media       	/chenry/public/modelsupport/media/Biolog-C-cytd
    -rr chenry    	       590	2015-05-11T05:40:22	media       	/chenry/public/modelsupport/media/Carbon-D-Glucose-6-Phosphate
    -rr chenry    	       588	2015-05-11T05:40:23	media       	/chenry/public/modelsupport/media/Sulfate-Thymine
    -rr chenry    	       588	2015-05-11T05:40:23	media       	/chenry/public/modelsupport/media/Phosphate-D-Glucose-1-Phosphate
    -rr chenry    	       572	2015-05-11T05:40:23	media       	/chenry/public/modelsupport/media/Phosphate-Uridine-5-Monophosphate
    -rr chenry    	       589	2015-05-11T05:40:23	media       	/chenry/public/modelsupport/media/Carbon-D-L-a-Glycerol-Phosphate
    -rr chenry    	       587	2015-05-11T05:40:25	media       	/chenry/public/modelsupport/media/Nitrogen-L-Isoleucine
    -rr chenry    	       586	2015-05-11T05:40:25	media       	/chenry/public/modelsupport/media/Nitrogen-L-Threonine
    -rr chenry    	       582	2015-05-11T05:40:25	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Leu
    -rr chenry    	       603	2015-05-11T05:40:26	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-D-mannosamine
    -rr chenry    	       578	2015-05-11T05:40:26	media       	/chenry/public/modelsupport/media/Carbon-Adenosine
    -rr chenry    	       581	2015-05-11T05:40:26	media       	/chenry/public/modelsupport/media/Sulfate-L-Djenkolic-Acid
    -rr chenry    	       592	2015-05-11T05:40:26	media       	/chenry/public/modelsupport/media/Sulfate-D-Aspartate
    -rr chenry    	       572	2015-05-11T05:40:27	media       	/chenry/public/modelsupport/media/Phosphate-Guanosine-5-Monophosphate
    -rr chenry    	       577	2015-05-11T05:40:27	media       	/chenry/public/modelsupport/media/Carbon-L-Xylose
    -rr chenry    	       579	2015-05-11T05:40:27	media       	/chenry/public/modelsupport/media/Carbon-Palatinose
    -rr chenry    	       588	2015-05-11T05:40:28	media       	/chenry/public/modelsupport/media/Carbon-a-Hydroxy-Butyric-Acid
    -rr chenry    	       573	2015-05-11T05:40:29	media       	/chenry/public/modelsupport/media/Carbon-3-Hydroxy-2-Butanone
    -rr chenry    	       588	2015-05-11T05:40:30	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-dna
    -rr chenry    	       590	2015-05-11T05:40:31	media       	/chenry/public/modelsupport/media/Phosphate-D-Glucose-6-Phosphate
    -rr chenry    	       582	2015-05-11T05:40:31	media       	/chenry/public/modelsupport/media/Sulfate-D-L-Ethionine
    -rr chenry    	       578	2015-05-11T05:40:31	media       	/chenry/public/modelsupport/media/Carbon-L-Arabitol
    -rr chenry    	       578	2015-05-11T05:40:32	media       	/chenry/public/modelsupport/media/Carbon-Urocanic-Acid
    -rr chenry    	       587	2015-05-11T05:40:33	media       	/chenry/public/modelsupport/media/Phosphate-Cytidine-2-3-Cyclic-Monophosphate
    -rr chenry    	       577	2015-05-11T05:40:33	media       	/chenry/public/modelsupport/media/Carbon-Butyric-Acid
    -rr chenry    	       580	2015-05-11T05:40:34	media       	/chenry/public/modelsupport/media/Carbon-Caproic-Acid
    -rr chenry    	       589	2015-05-11T05:40:34	media       	/chenry/public/modelsupport/media/Sulfate-L-Lyxose
    -rr chenry    	       572	2015-05-11T05:40:34	media       	/chenry/public/modelsupport/media/Phosphate-Cytidine-5-Monophosphate
    -rr chenry    	       573	2015-05-11T05:40:34	media       	/chenry/public/modelsupport/media/Carbon-D-Cellobiose
    -rr chenry    	       590	2015-05-11T05:40:35	media       	/chenry/public/modelsupport/media/Nitrogen-L-Phenylalanine
    -rr chenry    	       596	2015-05-11T05:40:35	media       	/chenry/public/modelsupport/media/Sulfate-L-Phenylalanine
    -rr chenry    	       589	2015-05-11T05:40:36	media       	/chenry/public/modelsupport/media/Phosphate-Carbamyl-Phosphate
    -rr chenry    	       578	2015-05-11T05:40:37	media       	/chenry/public/modelsupport/media/Carbon-Dihydroxy-Acetone
    -rr chenry    	       584	2015-05-11T05:40:37	media       	/chenry/public/modelsupport/media/Nitrogen-L-Alanine
    -rr chenry    	       584	2015-05-11T05:40:37	media       	/chenry/public/modelsupport/media/Carbon-D-Galacturonic-Acid
    -rr chenry    	       589	2015-05-11T05:40:37	media       	/chenry/public/modelsupport/media/Sulfate-Cytidine
    -rr chenry    	       578	2015-05-11T05:40:38	media       	/chenry/public/modelsupport/media/Nitrogen-Ammonia
    -rr chenry    	       578	2015-05-11T05:40:38	media       	/chenry/public/modelsupport/media/Carbon-L-Leucine
    -rr chenry    	       577	2015-05-11T05:40:38	media       	/chenry/public/modelsupport/media/Carbon-Pyruvic-Acid
    -rr chenry    	       575	2015-05-11T05:40:39	media       	/chenry/public/modelsupport/media/Carbon-D-Xylose
    -rr chenry    	       589	2015-05-11T05:40:39	media       	/chenry/public/modelsupport/media/Sulfate-Pyruvate
    -rr chenry    	       578	2015-05-11T05:40:39	media       	/chenry/public/modelsupport/media/Carbon-Stachyose
    -rr chenry    	       584	2015-05-11T05:40:40	media       	/chenry/public/modelsupport/media/Biolog-C-lac-S-gthrd
    -rr chenry    	       585	2015-05-11T05:40:41	media       	/chenry/public/modelsupport/media/Nitrogen-L-Arginine
    -rr chenry    	       578	2015-05-11T05:40:41	media       	/chenry/public/modelsupport/media/Carbon-D-Alanine
    -rr chenry    	       590	2015-05-11T05:40:42	media       	/chenry/public/modelsupport/media/Phosphate-6-Phospho-Gluconic-Acid
    -rr chenry    	       579	2015-05-11T05:40:42	media       	/chenry/public/modelsupport/media/Nitrogen-Urea
    -rr chenry    	       577	2015-05-11T05:40:42	media       	/chenry/public/modelsupport/media/Carbon-D-L-Malic-Acid
    -rr chenry    	       578	2015-05-11T05:40:42	media       	/chenry/public/modelsupport/media/Carbon-Itaconic-Acid
    -rr chenry    	       594	2015-05-11T05:40:43	media       	/chenry/public/modelsupport/media/Sulfate-2-Amino-2-deoxy-D-glucon
    -rr chenry    	       585	2015-05-11T05:40:49	media       	/chenry/public/modelsupport/media/Nitrogen-L-Cysteine
    -rr chenry    	       546	2015-05-11T05:40:49	media       	/chenry/public/modelsupport/media/Phosphate-D-Mannose-1-Phosphate
    -rr chenry    	       586	2015-05-11T05:40:49	media       	/chenry/public/modelsupport/media/Carbon-D-Galactonic-Acid-g-Lactone
    -rr chenry    	       563	2015-05-11T05:40:49	media       	/chenry/public/modelsupport/media/Biolog-C-ile-l-N-ile-l
    -rr chenry    	       579	2015-05-11T05:40:49	media       	/chenry/public/modelsupport/media/Carbon-Glyoxylic-Acid
    -rr chenry    	       691	2015-05-11T05:40:50	media       	/chenry/public/modelsupport/media/MR1Aerobic
    -rr chenry    	       582	2015-05-11T05:40:50	media       	/chenry/public/modelsupport/media/Sulfate-Carbon
    -rr chenry    	       587	2015-05-11T05:40:50	media       	/chenry/public/modelsupport/media/Sulfate-L-Cysteine-Sulfinic-Acid
    -rr chenry    	       577	2015-05-11T05:40:50	media       	/chenry/public/modelsupport/media/Carbon-D-Raffinose
    -rr chenry    	       587	2015-05-11T05:40:50	media       	/chenry/public/modelsupport/media/Sulfate-Mannan
    -rr chenry    	       588	2015-05-11T05:40:51	media       	/chenry/public/modelsupport/media/Sulfate-Ala-Leu
    -rr chenry    	       577	2015-05-11T05:40:51	media       	/chenry/public/modelsupport/media/Carbon-Fumaric-Acid
    -rr chenry    	       548	2015-05-11T05:40:52	media       	/chenry/public/modelsupport/media/Biolog-C-dna-P-dna
    -rr chenry    	       578	2015-05-11T05:40:53	media       	/chenry/public/modelsupport/media/Carbon-Glycolic-Acid
    -rr chenry    	       590	2015-05-11T05:40:53	media       	/chenry/public/modelsupport/media/Sulfate-L-Sorbose
    -rr chenry    	       576	2015-05-11T05:40:53	media       	/chenry/public/modelsupport/media/Carbon-Formic-Acid
    -rr chenry    	       592	2015-05-11T05:40:53	media       	/chenry/public/modelsupport/media/Sulfate-Methylamine
    -rr chenry    	       580	2015-05-11T05:40:54	media       	/chenry/public/modelsupport/media/Carbon-D-Glucose-Palsson
    -rr chenry    	       577	2015-05-11T05:40:54	media       	/chenry/public/modelsupport/media/Carbon-L-Tartaric-Acid
    -rr chenry    	       584	2015-05-11T05:40:54	media       	/chenry/public/modelsupport/media/Sulfate-Xanthine
    -rr chenry    	       594	2015-05-11T05:40:54	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-pro-l
    -rr chenry    	       583	2015-05-11T05:40:54	media       	/chenry/public/modelsupport/media/Carbon-2-Deoxy-Adenosine
    -rr chenry    	       596	2015-05-11T05:40:55	media       	/chenry/public/modelsupport/media/Carbon-b-Methyl-D-Galactoside
    -rr chenry    	       576	2015-05-11T05:40:55	media       	/chenry/public/modelsupport/media/Carbon-Gelatin
    -rr chenry    	       587	2015-05-11T05:40:55	media       	/chenry/public/modelsupport/media/Nitrogen-L-Tryptophan
    -rr chenry    	       590	2015-05-11T05:40:55	media       	/chenry/public/modelsupport/media/Sulfate-Succinate
    -rr chenry    	      1468	2015-05-11T05:40:55	media       	/chenry/public/modelsupport/media/ArgonneNMSMedia
    -rr chenry    	       588	2015-05-11T05:40:56	media       	/chenry/public/modelsupport/media/Sulfate-Gly-Met
    -rr chenry    	       576	2015-05-11T05:40:56	media       	/chenry/public/modelsupport/media/Carbon-Dulcitol
    -rr chenry    	       577	2015-05-11T05:40:57	media       	/chenry/public/modelsupport/media/Carbon-D-Serine
    -rr chenry    	       579	2015-05-11T05:40:58	media       	/chenry/public/modelsupport/media/Nitrogen-g-Amino-N-Butyric-Acid
    -rr chenry    	       591	2015-05-11T05:40:58	media       	/chenry/public/modelsupport/media/Sulfate-L-Methionine-Sulfoxide
    -rr chenry    	       590	2015-05-11T05:40:58	media       	/chenry/public/modelsupport/media/Sulfate-Laminarin
    -rr chenry    	       573	2015-05-11T05:40:58	media       	/chenry/public/modelsupport/media/Carbon-a-D-Lactose
    -rr chenry    	       577	2015-05-11T05:40:58	media       	/chenry/public/modelsupport/media/Carbon-L-Lysine
    -rr chenry    	       588	2015-05-11T05:40:59	media       	/chenry/public/modelsupport/media/Nitrogen-Hydroxylamine
    -rr chenry    	       583	2015-05-11T05:40:59	media       	/chenry/public/modelsupport/media/Sulfate-Taurocholic-Acid
    -rr chenry    	       580	2015-05-11T05:40:59	media       	/chenry/public/modelsupport/media/Carbon-L-Arabinose
    -rr chenry    	       590	2015-05-11T05:40:59	media       	/chenry/public/modelsupport/media/Sulfate-S-Lactate
    -rr chenry    	       587	2015-05-11T05:40:59	media       	/chenry/public/modelsupport/media/Phosphate-Guanosine-2-3-Cyclic-Monophosphate
    -rr chenry    	       573	2015-05-11T05:41:00	media       	/chenry/public/modelsupport/media/Biolog-C-acgam-N--acgam
    -rr chenry    	       584	2015-05-11T05:41:00	media       	/chenry/public/modelsupport/media/Nitrogen-Guanosine
    -rr chenry    	       588	2015-05-11T05:41:01	media       	/chenry/public/modelsupport/media/Sulfate-Oxalate
    -rr chenry    	       585	2015-05-11T05:41:01	media       	/chenry/public/modelsupport/media/Phosphate-Trimetaphosphate
    -rr chenry    	       589	2015-05-11T05:41:01	media       	/chenry/public/modelsupport/media/Sulfate-D-Serine
    -rr chenry    	       589	2015-05-11T05:41:01	media       	/chenry/public/modelsupport/media/Sulfate-Malonate
    -rr chenry    	       584	2015-05-11T05:41:01	media       	/chenry/public/modelsupport/media/Nitrogen-L-Leucine
    -rr chenry    	       577	2015-05-11T05:41:02	media       	/chenry/public/modelsupport/media/Sulfate-Thiosulfate
    -rr chenry    	       590	2015-05-11T05:41:02	media       	/chenry/public/modelsupport/media/Sulfate-Adenosine
    -rr chenry    	       587	2015-05-11T05:41:02	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetylneuraminate
    -rr chenry    	       588	2015-05-11T05:41:02	media       	/chenry/public/modelsupport/media/Sulfate-Formate
    -rr chenry    	       587	2015-05-11T05:41:03	media       	/chenry/public/modelsupport/media/Phosphate-Phospho-Glycolic-Acid
    -rr chenry    	       593	2015-05-11T05:41:03	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-ser-l
    -rr chenry    	       589	2015-05-11T05:41:03	media       	/chenry/public/modelsupport/media/Sulfate-Tween-80
    -rr chenry    	       579	2015-05-11T05:41:03	media       	/chenry/public/modelsupport/media/Carbon-D-Fructose
    -rr chenry    	       583	2015-05-11T05:41:03	media       	/chenry/public/modelsupport/media/Nitrogen-D-Lysine
    -rr chenry    	       586	2015-05-11T05:41:04	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Thr
    -rr chenry    	       595	2015-05-11T05:41:04	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-arg-l
    -rr chenry    	       577	2015-05-11T05:41:04	media       	/chenry/public/modelsupport/media/Carbon-L-Lyxose
    -rr chenry    	       597	2015-05-11T05:41:05	media       	/chenry/public/modelsupport/media/Nitrogen-N-Acetyl-D-Glucosamine
    -rr chenry    	       584	2015-05-11T05:41:05	media       	/chenry/public/modelsupport/media/Nitrogen-Thymidine
    -rr chenry    	       586	2015-05-11T05:41:05	media       	/chenry/public/modelsupport/media/Carbon-4-Hydroxy-Benzoic-Acid
    -rr chenry    	       578	2015-05-11T05:41:05	media       	/chenry/public/modelsupport/media/Carbon-Laminarin
    -rr chenry    	       581	2015-05-11T05:41:05	media       	/chenry/public/modelsupport/media/Carbon-L-Isoleucine
    -rr chenry    	       575	2015-05-11T05:41:06	media       	/chenry/public/modelsupport/media/Carbon-N-Acetyl-Neuraminic-Acid
    -rr chenry    	        38	2015-05-11T05:41:06	media       	/chenry/public/modelsupport/media/Empty
    -rr chenry    	       581	2015-05-11T05:41:06	media       	/chenry/public/modelsupport/media/Carbon-L-Methionine
    -rr chenry    	       584	2015-05-11T05:41:06	media       	/chenry/public/modelsupport/media/Phosphate-Phosphocreatine
    -rr chenry    	       578	2015-05-11T05:41:06	media       	/chenry/public/modelsupport/media/Carbon-D-Galactose
    -rr chenry    	       585	2015-05-11T05:41:07	media       	/chenry/public/modelsupport/media/Sulfate-Urea
    -rr chenry    	       594	2015-05-11T05:41:07	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-leu-l
    -rr chenry    	       580	2015-05-11T05:41:07	media       	/chenry/public/modelsupport/media/Carbon-L-Histidine
    -rr chenry    	       588	2015-05-11T05:41:07	media       	/chenry/public/modelsupport/media/Sulfate-sorbate
    -rr chenry    	       590	2015-05-11T05:41:08	media       	/chenry/public/modelsupport/media/Sulfate-Allantoin
    -rr chenry    	       594	2015-05-11T05:41:08	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-ala-l
    -rr chenry    	       562	2015-05-11T05:41:09	media       	/chenry/public/modelsupport/media/Biolog-C-glu-l-N-glu-l
    -rr chenry    	       578	2015-05-11T05:41:09	media       	/chenry/public/modelsupport/media/Carbon-Glycyl-L-Aspartic-Acid
    -rr chenry    	       596	2015-05-11T05:41:09	media       	/chenry/public/modelsupport/media/Carbon-a-Methyl-D-Galactoside
    -rr chenry    	       584	2015-05-11T05:41:09	media       	/chenry/public/modelsupport/media/Carbon-a-Keto-Valeric-Acid
    -rr chenry    	       577	2015-05-11T05:41:09	media       	/chenry/public/modelsupport/media/Carbon-L-Fucose
    -rr chenry    	       592	2015-05-11T05:41:10	media       	/chenry/public/modelsupport/media/Sulfate-D-Arabinose
    -rr chenry    	       582	2015-05-11T05:41:10	media       	/chenry/public/modelsupport/media/Sulfate-Hypotaurine
    -rr chenry    	       583	2015-05-11T05:41:10	media       	/chenry/public/modelsupport/media/Nitrogen-Cytosine
    -rr chenry    	       581	2015-05-11T05:41:10	media       	/chenry/public/modelsupport/media/Sulfate-L-Cysteine
    -rr chenry    	       585	2015-05-11T05:41:10	media       	/chenry/public/modelsupport/media/Nitrogen-Putrescine
    -rr chenry    	       583	2015-05-11T05:41:11	media       	/chenry/public/modelsupport/media/Nitrogen-L-Serine
    -rr chenry    	       578	2015-05-11T05:41:11	media       	/chenry/public/modelsupport/media/Carbon-i-Erythritol
    -rr chenry    	       597	2015-05-11T05:41:11	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-asn-l
    -rr chenry    	       579	2015-05-11T05:41:11	media       	/chenry/public/modelsupport/media/Carbon-m-Inositol
    -rr chenry    	       589	2015-05-11T05:41:11	media       	/chenry/public/modelsupport/media/Sulfate-Sebacic-acid
    -rr chenry    	       589	2015-05-11T05:41:12	media       	/chenry/public/modelsupport/media/Sulfate-L-Serine
    -rr chenry    	       573	2015-05-11T05:41:12	media       	/chenry/public/modelsupport/media/Phosphate-Thymidine-5-Monophosphate
    -rr chenry    	       591	2015-05-11T05:41:13	media       	/chenry/public/modelsupport/media/Sulfate-L-Arginine
    -rr chenry    	       593	2015-05-11T05:41:13	media       	/chenry/public/modelsupport/media/Sulfate-L-Asparagine
    -rr chenry    	       580	2015-05-11T05:41:13	media       	/chenry/public/modelsupport/media/Carbon-D-Aspartic-Acid
    -rr chenry    	       579	2015-05-11T05:41:13	media       	/chenry/public/modelsupport/media/Carbon-Propionic-Acid
    -rr chenry    	       589	2015-05-11T05:41:13	media       	/chenry/public/modelsupport/media/Sulfate-D-Valine
    -rr chenry    	       578	2015-05-11T05:41:14	media       	/chenry/public/modelsupport/media/Carbon-2-Deoxy-D-Ribose
    -rr chenry    	       588	2015-05-11T05:41:14	media       	/chenry/public/modelsupport/media/Phosphate-O-Phosphoryl-Ethanolamine
    -rr chenry    	       599	2015-05-11T05:41:14	media       	/chenry/public/modelsupport/media/Nitrogen-N-Acetyl-D-Galactosamine
    -rr chenry    	       588	2015-05-11T05:41:14	media       	/chenry/public/modelsupport/media/Nitrogen-D-Mannosamine
    -rr chenry    	       578	2015-05-11T05:41:14	media       	/chenry/public/modelsupport/media/Carbon-Lactulose
    -rr chenry    	       592	2015-05-11T05:41:15	media       	/chenry/public/modelsupport/media/Sulfate-L-Aspartate
    -rr chenry    	       575	2015-05-11T05:41:15	media       	/chenry/public/modelsupport/media/Phosphate-Uridine-3-Monophosphate
    -rr chenry    	       578	2015-05-11T05:41:15	media       	/chenry/public/modelsupport/media/Carbon-Succinic-Acid
    -rr chenry    	       587	2015-05-11T05:41:15	media       	/chenry/public/modelsupport/media/Nitrogen-D-Asparagine
    -rr chenry    	       585	2015-05-11T05:41:15	media       	/chenry/public/modelsupport/media/Nitrogen-L-Citrulline
    -rr chenry    	       572	2015-05-11T05:41:16	media       	/chenry/public/modelsupport/media/Phosphate-Adenosine-5-Monophosphate
    -rr chenry    	       589	2015-05-11T05:41:17	media       	/chenry/public/modelsupport/media/Sulfate-D-Lysine
    -rr chenry    	       590	2015-05-11T05:41:17	media       	/chenry/public/modelsupport/media/Sulfate-L-Leucine
    -rr chenry    	       596	2015-05-11T05:41:17	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-gln-l
    -rr chenry    	       579	2015-05-11T05:41:17	media       	/chenry/public/modelsupport/media/Carbon-D-Tagatose
    -rr chenry    	       589	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Sulfate-Glycogen
    -rr chenry    	       589	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Sulfate-S-Malate
    -rr chenry    	       595	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-ptrc
    -rr chenry    	       584	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Carbon-L-Phenylalanine
    -rr chenry    	       592	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Sulfate-2-Methylmaleate
    -rr chenry    	       591	2015-05-11T05:41:18	media       	/chenry/public/modelsupport/media/Sulfate-Palatinose
    -rr chenry    	       583	2015-05-11T05:41:19	media       	/chenry/public/modelsupport/media/Nitrogen-D-Valine
    -rr chenry    	       573	2015-05-11T05:41:19	media       	/chenry/public/modelsupport/media/Carbon-g-Amino-Butyric-Acid
    -rr chenry    	       591	2015-05-11T05:41:19	media       	/chenry/public/modelsupport/media/Sulfate-Glyoxylate
    -rr chenry    	       582	2015-05-11T05:41:19	media       	/chenry/public/modelsupport/media/Nitrogen-Guanine
    -rr chenry    	       586	2015-05-11T05:41:19	media       	/chenry/public/modelsupport/media/Sulfate-Butane-Sulfonic-Acid
    -rr chenry    	       601	2015-05-11T05:41:20	media       	/chenry/public/modelsupport/media/Sulfate-b-Methyl-D-Glucoside
    -rr chenry    	       576	2015-05-11T05:41:21	media       	/chenry/public/modelsupport/media/Carbon-Inosine
    -rr chenry    	       583	2015-05-11T05:41:21	media       	/chenry/public/modelsupport/media/Phosphate-Phosphoryl-Choline
    -rr chenry    	       582	2015-05-11T05:41:21	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Gln
    -rr chenry    	       577	2015-05-11T05:41:21	media       	/chenry/public/modelsupport/media/Carbon-Sebacic-Acid
    -rr chenry    	       580	2015-05-11T05:41:22	media       	/chenry/public/modelsupport/media/Carbon-D-Arabinose
    -rr chenry    	       584	2015-05-11T05:41:22	media       	/chenry/public/modelsupport/media/Nitrogen-D-Alanine
    -rr chenry    	       601	2015-05-11T05:41:22	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-L-glutamate
    -rr chenry    	       591	2015-05-11T05:41:22	media       	/chenry/public/modelsupport/media/Nitrogen-e-Amino-N-Caproic-Acid
    -rr chenry    	       578	2015-05-11T05:41:22	media       	/chenry/public/modelsupport/media/Carbon-L-Lactic-Acid
    -rr chenry    	       211	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/NoBounds
    -rr chenry    	       587	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/Biolog-C-lac-S-tsul
    -rr chenry    	       583	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/Nitrogen-D-Serine
    -rr chenry    	       579	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/Carbon-L-Arginine
    -rr chenry    	       582	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/Nitrogen-Adenine
    -rr chenry    	       580	2015-05-11T05:41:23	media       	/chenry/public/modelsupport/media/Carbon-D-Glucuronic-Acid
    -rr chenry    	       585	2015-05-11T05:41:24	media       	/chenry/public/modelsupport/media/Phosphate-Adenosine-2-Monophosphate
    -rr chenry    	       590	2015-05-11T05:41:25	media       	/chenry/public/modelsupport/media/Carbon-Chondroitin-Sulfate-C
    -rr chenry    	       580	2015-05-11T05:41:25	media       	/chenry/public/modelsupport/media/Carbon-Maltotriose
    -rr chenry    	       620	2015-05-11T05:41:25	media       	/chenry/public/modelsupport/media/Carbon-D-Glucose
    -rr chenry    	       697	2015-05-11T05:41:25	media       	/chenry/public/modelsupport/media/MR1Anaerobic
    -rr chenry    	       577	2015-05-11T05:41:25	media       	/chenry/public/modelsupport/media/Carbon-L-Serine
    -rr chenry    	       575	2015-05-11T05:41:26	media       	/chenry/public/modelsupport/media/Phosphate-Adenosine-3-Monophosphate
    -rr chenry    	       593	2015-05-11T05:41:26	media       	/chenry/public/modelsupport/media/Sulfate-Ethanolamine
    -rr chenry    	       571	2015-05-11T05:41:26	media       	/chenry/public/modelsupport/media/Phosphate-Guanosine-3-Monophosphate
    -rr chenry    	       559	2015-05-11T05:41:26	media       	/chenry/public/modelsupport/media/Biolog-C-cytd-N-cytd
    -rr chenry    	       584	2015-05-11T05:41:26	media       	/chenry/public/modelsupport/media/Carbon-a-Keto-Butyric-Acid
    -rr chenry    	       591	2015-05-11T05:41:27	media       	/chenry/public/modelsupport/media/Sulfate-Mannitol
    -rr chenry    	       588	2015-05-11T05:41:27	media       	/chenry/public/modelsupport/media/Sulfate-Inosine
    -rr chenry    	       588	2015-05-11T05:41:27	media       	/chenry/public/modelsupport/media/Phosphate-Phosphoenol-Pyruvate
    -rr chenry    	       590	2015-05-11T05:41:27	media       	/chenry/public/modelsupport/media/Nitrogen-Ala-Gly
    -rr chenry    	       589	2015-05-11T05:41:27	media       	/chenry/public/modelsupport/media/Sulfate-Methane-Sulfonic-Acid
    -rr chenry    	       584	2015-05-11T05:41:28	media       	/chenry/public/modelsupport/media/Nitrogen-L-Ornithine
    -rr chenry    	       586	2015-05-11T05:41:28	media       	/chenry/public/modelsupport/media/Nitrogen-L-Histidine
    -rr chenry    	       587	2015-05-11T05:41:28	media       	/chenry/public/modelsupport/media/Phosphate-Uridine-2-3-Cyclic-Monophosphate
    -rr chenry    	       584	2015-05-11T05:41:29	media       	/chenry/public/modelsupport/media/Phosphate-Phospho-L-Arginine
    -rr chenry    	       556	2015-05-11T05:41:29	media       	/chenry/public/modelsupport/media/Biolog-C-lac-S-so3
    -rr chenry    	       573	2015-05-11T05:41:29	media       	/chenry/public/modelsupport/media/Carbon-D-Trehalose
    -rr chenry    	       582	2015-05-11T05:41:30	media       	/chenry/public/modelsupport/media/Nitrogen-Gly-Met
    -rr chenry    	       574	2015-05-11T05:41:30	media       	/chenry/public/modelsupport/media/Carbon-Arbutin
    -rr chenry    	       588	2015-05-11T05:41:30	media       	/chenry/public/modelsupport/media/Sulfate-Gly-Gln
    -rr chenry    	       584	2015-05-11T05:41:30	media       	/chenry/public/modelsupport/media/Carbon-1-2-Propanediol
    -rr chenry    	       579	2015-05-11T05:41:30	media       	/chenry/public/modelsupport/media/Sulfate-Thiourea
    -rr chenry    	       586	2015-05-11T05:41:31	media       	/chenry/public/modelsupport/media/Nitrogen-Methylamine
    -rr chenry    	       577	2015-05-11T05:41:31	media       	/chenry/public/modelsupport/media/Carbon-Malonic-Acid
    -rr chenry    	       593	2015-05-11T05:41:31	media       	/chenry/public/modelsupport/media/Sulfate-L-Homoserine
    -rr chenry    	       576	2015-05-11T05:41:32	media       	/chenry/public/modelsupport/media/Carbon-Adonitol
    -rr chenry    	       591	2015-05-11T05:41:32	media       	/chenry/public/modelsupport/media/Sulfate-Propanoate
    -rr chenry    	       596	2015-05-11T05:41:33	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-thr-l
    -rr chenry    	       575	2015-05-11T05:41:33	media       	/chenry/public/modelsupport/media/Carbon-Inulin
    -rr chenry    	       584	2015-05-11T05:41:33	media       	/chenry/public/modelsupport/media/Carbon-D-L-Citramalic-Acid
    -rr chenry    	       591	2015-05-11T05:41:34	media       	/chenry/public/modelsupport/media/Sulfate-D-Tagatose
    -rr chenry    	       591	2015-05-11T05:41:34	media       	/chenry/public/modelsupport/media/Sulfate-L-Citrulline
    -rr chenry    	       577	2015-05-11T05:41:34	media       	/chenry/public/modelsupport/media/Carbon-L-Valine
    -rr chenry    	       581	2015-05-11T05:41:34	media       	/chenry/public/modelsupport/media/Carbon-L-Homoserine
    -rr chenry    	       575	2015-05-11T05:41:34	media       	/chenry/public/modelsupport/media/Carbon-2-Hydroxy-Benzoic-Acid
    -rr chenry    	       577	2015-05-11T05:41:35	media       	/chenry/public/modelsupport/media/Carbon-D-Sorbitol
    -rr chenry    	      3649	2015-05-11T05:41:35	media       	/chenry/public/modelsupport/media/SP4
    -rr chenry    	       577	2015-05-11T05:41:35	media       	/chenry/public/modelsupport/media/Carbon-Tween-20
    -rr chenry    	       591	2015-05-11T05:41:35	media       	/chenry/public/modelsupport/media/Sulfate-Ethylamine
    -rr chenry    	       588	2015-05-11T05:41:35	media       	/chenry/public/modelsupport/media/Sulfate-Salicin
    -rr chenry    	       586	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Phosphate-O-Phospho-L-Tyrosine
    -rr chenry    	       581	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Carbon-Ethanolamine
    -rr chenry    	       585	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Nitrogen-Xanthosine
    -rr chenry    	       589	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Sulfate-Fumarate
    -rr chenry    	       587	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Sulfate-2-1-beta-D-Fructosyl-n
    -rr chenry    	       592	2015-05-11T05:41:36	media       	/chenry/public/modelsupport/media/Sulfate-L-Threonine
    -rr chenry    	       579	2015-05-11T05:41:37	media       	/chenry/public/modelsupport/media/Carbon-Putrescine
    -rr chenry    	       598	2015-05-11T05:41:37	media       	/chenry/public/modelsupport/media/Phosphate-2-Deoxy-D-Glucose-6-Phosphate
    -rr chenry    	       580	2015-05-11T05:41:37	media       	/chenry/public/modelsupport/media/Carbon-D-Threonine
    -rr chenry    	       575	2015-05-11T05:41:37	media       	/chenry/public/modelsupport/media/Carbon-Pectin
    -rr chenry    	       240	2015-05-11T05:41:37	media       	/chenry/public/modelsupport/media/MethanogenMedia
    -rr chenry    	       576	2015-05-11T05:41:38	media       	/chenry/public/modelsupport/media/Carbon-Glycine
    -rr chenry    	       602	2015-05-11T05:41:38	media       	/chenry/public/modelsupport/media/Sulfate-D-Glucose-6-phosphate
    -rr chenry    	       588	2015-05-11T05:41:38	media       	/chenry/public/modelsupport/media/Sulfate-Nitrate
    -rr chenry    	       580	2015-05-11T05:41:38	media       	/chenry/public/modelsupport/media/Carbon-Gentiobiose
    -rr chenry    	       578	2015-05-11T05:41:39	media       	/chenry/public/modelsupport/media/Carbon-L-Sorbose
    -rr chenry    	       578	2015-05-11T05:41:39	media       	/chenry/public/modelsupport/media/Carbon-Acetamide
    -rr chenry    	       581	2015-05-11T05:41:39	media       	/chenry/public/modelsupport/media/Sulfate-D-Cysteine
    -rr chenry    	       520	2015-05-11T05:41:39	media       	/chenry/public/modelsupport/media/Biolog-C-dna-N-dna-P-dna
    -rr chenry    	       577	2015-05-11T05:41:39	media       	/chenry/public/modelsupport/media/Carbon-Glycerol
    -rr chenry    	       596	2015-05-11T05:41:40	media       	/chenry/public/modelsupport/media/Sulfate-D-Galacturonate
    -rr chenry    	       590	2015-05-11T05:41:40	media       	/chenry/public/modelsupport/media/Sulfate-Itaconate
    -rr chenry    	       578	2015-05-11T05:41:40	media       	/chenry/public/modelsupport/media/Carbon-a-D-Glucose
    -rr chenry    	       582	2015-05-11T05:41:41	media       	/chenry/public/modelsupport/media/Nitrogen-Thymine
    -rr chenry    	       585	2015-05-11T05:41:41	media       	/chenry/public/modelsupport/media/Phosphate-Cytidine-3-5-Cyclic-Monophosphate
    -rr chenry    	       591	2015-05-11T05:41:42	media       	/chenry/public/modelsupport/media/Sulfate-L-Tyrosine
    -rr chenry    	       584	2015-05-11T05:41:42	media       	/chenry/public/modelsupport/media/Carbon-Oxalomalic-Acid
    -rr chenry    	       586	2015-05-11T05:41:42	media       	/chenry/public/modelsupport/media/Nitrogen-Met-Ala
    -rr chenry    	       589	2015-05-11T05:41:42	media       	/chenry/public/modelsupport/media/Carbon-b-Hydroxy-Butyric-Acid
    -rr chenry    	       587	2015-05-11T05:41:43	media       	/chenry/public/modelsupport/media/Sulfate-N-Acetyl-L-Cysteine
    -rr chenry    	       596	2015-05-11T05:41:43	media       	/chenry/public/modelsupport/media/Biolog-C-lac-N-asp-l
    -rr chenry    	       589	2015-05-11T05:41:43	media       	/chenry/public/modelsupport/media/Phosphate-D-L-a-Glycerol-Phosphate
    -rr chenry    	       578	2015-05-11T05:41:43	media       	/chenry/public/modelsupport/media/Carbon-Amygdalin
    -rr chenry    	       577	2015-05-11T05:41:43	media       	/chenry/public/modelsupport/media/Carbon-D-Tartaric-Acid
    -rr chenry    	       587	2015-05-11T05:41:44	media       	/chenry/public/modelsupport/media/Sulfate-Pectin
    -rr chenry    	       578	2015-05-11T05:41:45	media       	/chenry/public/modelsupport/media/Carbon-L-Ornithine
    -rr chenry    	       587	2015-05-11T05:41:45	media       	/chenry/public/modelsupport/media/Nitrogen-L-Homoserine
    -rr chenry    	       588	2015-05-11T05:41:45	media       	/chenry/public/modelsupport/media/Sulfate-Glycine
    -rr chenry    	       594	2015-05-11T05:41:45	media       	/chenry/public/modelsupport/media/Nitrogen-d-Amino-N-Valeric-Acid
    -rr chenry    	       585	2015-05-11T05:41:45	media       	/chenry/public/modelsupport/media/Sulfate-D-Glucosamine
    -rr chenry    	       593	2015-05-11T05:41:46	media       	/chenry/public/modelsupport/media/Sulfate-5-Oxoproline
    -rr chenry    	       592	2015-05-11T05:41:46	media       	/chenry/public/modelsupport/media/Phosphate-D-Glucosamine-6-Phosphate
    -rr chenry    	       562	2015-05-11T05:41:46	media       	/chenry/public/modelsupport/media/Biolog-C-thr-l-N-thr-l
    -rr chenry    	       593	2015-05-11T05:41:46	media       	/chenry/public/modelsupport/media/Sulfate-L-Tryptophan
    -rr chenry    	       581	2015-05-11T05:41:46	media       	/chenry/public/modelsupport/media/Carbon-Acetoacetic-Acid
    -rr chenry    	       590	2015-05-11T05:41:47	media       	/chenry/public/modelsupport/media/Carbon-Chondroitin
    -rr chenry    	       590	2015-05-11T05:41:47	media       	/chenry/public/modelsupport/media/Sulfate-Formamide
    -rr chenry    	       583	2015-05-11T05:41:47	media       	/chenry/public/modelsupport/media/Nitrogen-Agmatine
    -rr seaver    	       438	2016-01-29T22:10:40	media       	/chenry/public/modelsupport/media/PlantHeterotrophicMedia
    -rr seaver    	       438	2016-01-30T06:24:33	media       	/chenry/public/modelsupport/media/PlantAutotrophicMedia
    -rr seaver    	       354	2016-08-03T04:25:27	media       	/chenry/public/modelsupport/media/PlantSandboxMedia


Get the metadata for an object in the workspace with
``get_workspace_object_metadata()``. The metadata for an object can
include additional information about the contents or attributes of the
object.

.. code:: ipython2

    mackinac.get_workspace_object_meta('/chenry/public/modelsupport/media/Nitrogen-Uric-Acid')




.. parsed-literal::

    [u'Nitrogen-Uric-Acid',
     u'media',
     u'/chenry/public/modelsupport/media/',
     u'2015-05-11T05:39:04',
     u'0918D468-F7A0-11E4-AA0D-729D682E0674',
     u'chenry',
     580,
     {u'isDefined': 1,
      u'isMinimal': 1,
      u'name': u'Nitrogen-Uric Acid',
      u'source_id': u'Nitrogen-Uric Acid',
      u'type': u'biolog'},
     {u'is_folder': 0},
     u'r',
     u'r',
     u'']



Get the data in an object with ``get_workspace_object_data()``. The data
for an object can be large so use caution with this function. By
default, the object data is assumed to be in JSON format. Set the
``json_data=False`` parameter if the object data is not in JSON format.

.. code:: ipython2

    mackinac.get_workspace_object_data('/chenry/public/modelsupport/media/Nitrogen-Uric-Acid', json_data=False)




.. parsed-literal::

    u'id\tname\tconcentration\tminflux\tmaxflux\ncpd00027\tD-Glucose\t0.001\t-100\t5\ncpd00300\tUrate\t0.001\t-100\t5\ncpd00009\tPhosphate\t0.001\t-100\t5\ncpd00048\tSulfate\t0.001\t-100\t5\ncpd00063\tCa2+\t0.001\t-100\t100\ncpd00011\tCO2\t0.001\t-100\t0\ncpd10516\tfe3\t0.001\t-100\t100\ncpd00067\tH+\t0.001\t-100\t100\ncpd00001\tH2O\t0.001\t-100\t100\ncpd00205\tK+\t0.001\t-100\t100\ncpd00254\tMg\t0.001\t-100\t100\ncpd00971\tNa+\t0.001\t-100\t100\ncpd00007\tO2\t0.001\t-100\t100\ncpd00099\tCl-\t0.001\t-100\t100\ncpd00058\tCu2+\t0.001\t-100\t100\ncpd00149\tCo2+\t0.001\t-100\t100\ncpd00030\tMn2+\t0.001\t-100\t100\ncpd00034\tZn2+\t0.001\t-100\t100\ncpd10515\tFe2+\t0.001\t-100\t100\n'



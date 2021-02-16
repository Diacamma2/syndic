Les dépenses
============

     Menu *Copropriéte/Gestion/Les dépenses*.
     
Depuis cette liste des dépenses, vous pouvez gérer une dépense de copropriété et en créer une nouvelle via le bouton "Ajouter".

Une fois précisés la date et le descriptif de cette dépense, cliquez sur "Ok" afin qu'une nouvelle fiche de dépense soit créée. 
Dans la nouvelle fenêtre, indiquez le fournisseur concerné par la nouvelle dépense. Celui-ci doit être un tiers référencé pour ce qui est des dépenses. S'il ne figure pas dans la liste des contacts, ajoutez-le avec le bouton "+ Créer".
Ajoutez dans cette fiche les détails de dépense en spécifiant pour chacun : la catégorie de dépenses concernée, la désignation du détail, le compte de charges à mouvementer et le montant du détail.

    .. image:: expense.png

Une fiche de dépense peut prendre, pour votre gestion, un ensemble de status.
Avec ce schéma, vous pouvez comprendre comment les statuts peuvent s'enchainner :

    .. image:: expenseworkflow.png
    
Voici, ici, une description plus précise de ces status.

 * En création

 	Dans cet état, la fiche peut être complétement modifiée : description, date, type (facture ou avoir fournisseur), tiers, détails.
 	Par contre, aucun règlement ne peut être saisi.
 	Au niveau comptable, aucune écriture n'est alors générée.
 	A cette étape, il est encore possible de supprimer la fiche.
 	 
 * En attente

 	Proche de l'état précédent, par contre il n'est plus possible de supprimer la fiche et un numéro unique lui est attribuée.
 	Il n'est plus possible de changer son tiers et son type par contre les règlements peuvent être saisi.
 	Au niveau comptable, seule la saisi des règlements sont traduit en écriture comptable (au brouillard).

 * Validé

 	Plus aucune modification n'est possible à part l'ajout de nouveaux règlements.
 	En comptabilité, des écritures relatif aux détails sont générées au brouillard.

 * Cloturé

 	La fiche est totalement non modifiable.
 	En comptabilité, l'ensemble des écritures liées à cette dépense sont alors validées.

 * Annulé

 	C'est un état de conservation d'historique.
 	Plus aucune modification n'est possible.
 	Il n'y a plus de règlement (supprimés au changement d'état)
 	Les écritures comptables sont également supprimées.



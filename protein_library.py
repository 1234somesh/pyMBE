import numpy as np
import math as mt
import parameters as param
from parameters import particle
    
class residue:

    def __init__(self, name):

        self.name=name

    bondl=None
    k=None
    part=[]
    ids=[]


class molecule:

    N = None
    Nm = None
    ids = []
    bondl = None
    k = None
    model = None
     

    def __init__(self, sequence, model=None, param_custom=None, pKa_set=None, pKa_custom=None):


        model_param=None
        model_dict={}
    
        if model is not None:

            model_list=get_subclasses(param)

            # Get the model parameters

            for param_set in model_list:

                if param_set.name is not None:
                    
                    if model.lower() == param_set.name.lower():

                        model_param=param_set

            if model_param is None:

                model_names=get_modelnames()
                raise ValueError("Unknown model chosen: ", model, ". Valid options are ", model_names)
            # Get a list of model parameters
            
            list_model=get_attributes(model_param)

            for par in list_model:

                model_dict[par[0]]=par[1]

            # Get valid keys for the model

            model_actors=get_particles(model_param)
            keys=[]

            for actor in model_actors:
       
                keys.append(actor.name)
                
        else:
            
            keys=list(param.general.aminoacid.values())
               
        # Load Custom parameters if any

        # Check that the custom parameters are in the proper format:

        names_custom=[]
        
        if  param_custom is not None:

            if isinstance(param_custom, param.custom_parameters()):

                if model_param is not None:
                    
                # Overwrite model parameters by custom ones

                    list_custom=get_attributes(param_custom)
                    custom_dict={}
            
                    for par in list_custom:

                        custom_dict[par[0]]=par[1]

                    for atr in custom_dict.keys():

                        if custom_dict[atr] is not None:

                            if isinstance(custom_dict[atr], param.particle):
                                    
                                if atr in model_dict.keys():

                                    part_custom=get_attributes(custom_dict[atr])

                                    for par in part_custom:

                                        if par[1] is not None:

                                            setattr(model_dict[atr],par[0],par[1])

                                else:

                                    setattr(model_param,atr,custom_dict[atr])

                            else:
                                
                                setattr(model_param,atr,custom_dict[atr])
                                

                else:

                    model_param=param_custom

            else:

                raise ValueError("Unrecognized format for the custom parameters. Please, use the library function 'setup_custom_parameters' to define your custom parameters")
        

        if pKa_custom is not None:

            for key in pKa_custom.keys():

                keys.append(key)
        
        clean_sequence=sequence_parser(sequence, keys)
        
        # Import the pKa values

        param_pKa_set=get_subclasses(param.pKa_set)
        names_pKa_set=[]

        for sets in param_pKa_set:
            
            names_pKa_set.append(sets.name)

        if pKa_set is None:

            pKa_set=param.pKa_set.Hass.pKa

        elif isinstance(pKa_set, str):

            for sets in param_pKa_set:

                if (pKa_set.lower() == sets.name.lower()):

                    pKa_set=sets.pKa
                    break

            if not isinstance(pKa_set,dict):

                raise ValueError("Unknown key provided for a pKa set, valid options are " , names_pKa_set)
            
        else:
        

            raise ValueError("The desired pKa set must be given as a string, valid options are ", names_pKa_set)

        if pKa_custom is not None:

            if isinstance(pKa_custom,dict):

                for key in pKa_custom.keys():

                    pKa_set[key]=pKa_custom[key]

            else:

                raise ValueError("The custom pKa-values must be provided in a dictionary")

        # Create an object residue per each residue in sequence

        self.sequence=[]

        for res in clean_sequence:

            monomer=residue(name=res)
            self.sequence.append(monomer)

        # Set-up the model

        if model_param is None:

            # If no model nor custom parameters are given, create one bead particle per residue

            for res in self.sequence:

                bead=particle()
                bead.name=res.name
                bead_list=[]
                
                # If the residue has a pKa value list in the pKa_set put in the bead

                if res.name in pKa_set.keys():

                    bead.pKa=pKa_set[res.name]

                bead_list.append(bead)
                res.part=bead_list
        
        else:

            self.model=model_param
            
            if model_param.beads_per_residue is None:

                Tbead = 1

            else:

                Tbead = model_param.beads_per_residue

            param_part=get_particles(model_param)
            model_keys=[]

            for p_set in param_part:

                model_keys.append(p_set.name)

            for res in self.sequence:

                bead_list=[]

                if model_param.side_chain is None:

                    side_list=[]

                else:

                    side_list=model_param.side_chain.copy()


                for nbead in range(Tbead):

                    if (nbead == 0):

                        if model_param.principal_chain is None or model_param.principal_chain ==  'sequence':
                            bead_unparameterized=True

                            for p_set in param_part:

                                if (p_set.name == res.name):

                                    bead=p_set
                                    bead_unparameterized=False
                                    
                            if bead_unparameterized:

                                bead=particle()
                                bead.name=res.name

                            if res.name in pKa_set.keys():

                                bead.pKa=pKa_set[res.name]

                                    
                        elif model_param.principal_chain in model_keys:

                            for p_set in param_part:

                                if (p_set.name == model_param.principal_chain):

                                    bead=p_set

                                    if model_param.principal_chain in pKa_set.keys():

                                        bead.pKa=pKa_set[res.name]

                        
                        else:

                            raise ValueError("Unknown key for the principal chain: ", model_param.principal_chain)
                        
                        bead_list.append(bead)

                    else:


                        if len(side_list) == 0:

                            bead=particle()
                            bead_list.append(bead)

                        else:

                            bead_name=side_list[0]
                            bead_unparameterized=True

                            if bead_name == "sequence":
                                name= res.name
                                for p_set in param_part:

                                    if (p_set.name == name):

                                        bead=p_set
                                        bead_unparameterized=False
                                

                            elif bead_name in model_keys:
                                name=bead_name

                                for p_set in param_part:

                                    if (p_set.name == name):

                                        bead=p_set
                                        bead_unparameterized=False
                        
                            else:

                                raise ValueError("Unknown key for the side chain: ", bead_name)

                            if bead_unparameterized:

                                bead=particle()
                                bead.name=name

                            if bead_name in pKa_set.keys():

                                bead.pKa=pKa_set[bead_name]

                            bead_list.append(bead)
                            side_list.remove(bead_name)
                                
                    
                res.part=bead_list


def sequence_parser(sequence, keys=param.general.aminoacid.values()):
    '''
    Reads the input residue sequence and
    1) Checks that all residues are in the parameters key
    2) Transforms the aminoacids on the sequence from three letter to one letter format

    Input:
    sequence: (string or list) aminoacid sequence

    Output:
    clean_sequence: (string) 

    '''

    clean_sequence=[]
    
    if isinstance(sequence, str):
                
        if (sequence.find("-") != -1):

            splited_sequence=sequence.split("-")

            for residue in splited_sequence:

                if len(residue) == 1:

                    if residue in keys:

                        residue_ok=residue

                    else:

                        if residue.upper() in keys:

                            residue_ok=residue.upper()

                        else:

                            raise ValueError("Unknown one letter code for a residue given: ", residue, " please review the input sequence")

                    clean_sequence.append(residue_ok)
                
                else:

                    if residue in keys:

                        clean_sequence.append(residue)

                    else:

                        if (residue.upper() in param.general.aminoacid.keys()):

                            clean_sequence.append(param.general.aminoacid[residue.upper()])

                        else:

                            raise ValueError("Unknown  code for a residue: ", residue, " please review the input sequence")

        else:

            for residue in sequence:

                if residue in keys:

                    residue_ok=residue

                else:

                    if residue.upper() in keys:

                        residue_ok=residue.upper()

                    else:

                        raise ValueError("Unknown one letter code for a residue: ", residue, " please review the input sequence")

                clean_sequence.append(residue_ok)

    if isinstance(sequence, list):

        for residue in sequence:
               
                if residue in keys:

                    residue_ok=residue

                else:

                    if residue.upper() in keys:

                        residue_ok=residue.upper()

                    elif (residue.upper() in param.general.aminoacid.keys()):

                        clean_sequence.append(param.general.aminoacid[residue.upper()])

                    else:

                        raise ValueError("Unknown code for a residue: ", residue, " please review the input sequence")

                clean_sequence.append(residue_ok)

    return clean_sequence

def create_protein(system, protein, initial_state='neutral'):
    '''
    Creates a protein chain in the system with the sequence stored in protein, joined by harmonic_bond)
    Inputs:
    system: espresso class object with all system variables
    protein: class object as defined in this library
    '''
    
    import espressomd
    from espressomd import interactions

    param=parameters()

    if initial_state.lower() not in ['neutral', 'charged']:

        raise ValueError("Unvalid key for the initial state of the residue, valid options are 'neutral' or 'charged'. Key given: ",  initial_state)

    if protein.N is None:

        protein.N=1

    # Create a director vector for the principal chain

    backbone_vec=generate_trialvectors(protein.bondl.to('sigma').magnitude)

    # Create the harmonic bond for the principal chain

    backbone_bond = interactions.HarmonicBond(k=protein.k.to('sigma**-2').magnitude, r_0=protein.bondl.to('sigma').magnitude)
    
    system.bonded_inter.add(backbone_bond)
    # If there are other particles in system, the first id = max(current ids) +1 else first id = 0

    if  not system.part[:].id:

        bead_id=0

    else:

        bead_id=max(system.part[:].id)

    # create the protein chains in the espresso system

    for pep_chain in range(protein.N):

        first_monomer=True
        ids_chain=[]

        for residue in protein.sequence:

            n_bead=0
            list_ids_aa=residue.ids.copy()
            ids_aa=[]

            for bead in residue.part:

                bead_id+=1
                list_ids_bead=bead.ids.copy()

                if initial_state.lower() == 'charged':

                    if initial_state.lower() in bead.q.keys():

                        state=initial_state

                    else:
                        
                        state='neutral'
                else:

                    state=initial_state

                if first_monomer: # The first monomer is placed in a random place of the simulation box

                    first_monomer=False
                    pos_backbone=np.random.random((1, 3)) *np.copy(system.box_l)
                    id_backbone=bead_id
                    name_backbone=residue.name
                    system.part.add(id=[bead_id], pos=pos_backbone, type=[bead.type[state]], q=[bead.q[state]])
                    bead.state=state
                    bead.N+=1
                    list_ids_bead.append([bead_id])
                    bead.ids=list_ids_bead.copy()
                    ids_aa.append(bead_id)
                    ids_chain.append(bead_id)

                else:

                    if n_bead ==0:

                        pos_backbone+=backbone_vec
                        system.part.add(id=[bead_id], pos=pos_backbone, type=[bead.type[state]], q=[bead.q[state]])
                        
                        if (protein.beads_per_monomer == 1):

                            sidechain_bond = interactions.HarmonicBond(k=residue.k.to('sigma**-2').magnitude, r_0=residue.bondl.to('sigma').magnitude)
                            system.bonded_inter.add(sidechain_bond)
                            system.part[bead_id].add_bond((sidechain_bond, id_backbone))

                        else:


                            if (name_backbone =="n") or ( residue.name == "n"):

                                sidechain_bond = interactions.HarmonicBond(k=model_param.k["n"].to('sigma**-2').magnitude, r_0=model_param.bondl["n"].to('sigma').magnitude)
                                system.bonded_inter.add(sidechain_bond)
                                system.part[bead_id].add_bond((sidechain_bond, id_backbone))

                            elif (name_backbone =="c") or ( residue.name == "c"):
                                sidechain_bond = interactions.HarmonicBond(k=model_param.k["c"].to('sigma**-2').magnitude, r_0=model_param.bondl["c"].to('sigma').magnitude)
                                system.bonded_inter.add(sidechain_bond)
                                system.part[bead_id].add_bond((sidechain_bond, id_backbone))

                            else:

                                system.part[bead_id].add_bond((backbone_bond, id_backbone))
                        
                        list_ids_bead.append([bead_id])
                        bead.ids=list_ids_bead.copy()
                        bead.N+=1
                        bead.state=state
                        ids_aa.append(bead_id)
                        ids_chain.append(bead_id)
                        id_backbone=bead_id
                        name_backbone=residue.name

                    elif n_bead ==1:
                        
                        
                        rand_vec=generate_trialvectors(1)
                        sidechain_vec=np.cross(rand_vec,backbone_vec)
                        r = mt.sqrt(sum(x*x for x in sidechain_vec))
                        sidechain=np.array([x/r for x in sidechain_vec])
                        sidechain_vec=sidechain_vec*residue.bondl.to('sigma').magnitude
                        pos_sidechain=pos_backbone+sidechain_vec
                        system.part.add(id=[bead_id], pos=pos_sidechain, type=[bead.type[state]], q=[bead.q[state]])
                        sidechain_bond = interactions.HarmonicBond(k=residue.k.to('sigma**-2').magnitude, r_0=residue.bondl.to('sigma').magnitude)
                        system.bonded_inter.add(sidechain_bond)
                        system.part[bead_id].add_bond((sidechain_bond, id_backbone))
                        list_ids_bead.append([bead_id])
                        bead.state=state
                        bead.N+=1
                        bead.ids=list_ids_bead.copy()
                        ids_aa.append(bead_id)
                        ids_chain.append(bead_id)
                
                n_bead+=1
            
            list_ids_aa.append(ids_aa)
            residue.ids=list_ids_aa.copy()
        protein.ids.append(ids_chain)

    return 



def count_titrable_groups(protein):
    """
    Counts the number of titrable groups in the protein object

    Input:
    protein: class object as defined in this library, attributes:

    Output:
    N_ti: (int) number of titrable groups in the sequence
    """

    N_ti=0

    for residue in protein.sequence:

        if residue.pKa is not None:

            N_ti+=1

    N_ti*=protein.N

    return N_ti

def setup_protein_acidbase_reactions(RE, protein, cation):
    """
    Set up the Acid/Base reactions for acidic/basidic residues in protein. The reaction steps are done following the constant pH ensamble procedure. 

    Inputs:
    RE: instance of the espresso class reaction_ensemble.ConstantpHEnsemble
    protein: class object as defined in this library, attributes:
    cation: class objects of the cations,  with the following attributes:
        q: (int) charge of the ion
        type: (int) type of the ion
    """

    reaction_absent={}

    for group in param.general.pka_hass.keys():
        
        reaction_absent[group]=True

    for residue in protein.sequence:

        if residue.pKa is not None:
        
            for bead in residue.part:

                if (reaction_absent[residue.name] and "charged" in bead.q.keys()): 

                    if (bead.q["charged"] == 1) : # Basic residue
                        
                        RE.add_reaction(gamma=10**-residue.pKa,
                            reactant_types=[bead.type["charged"]],
                            reactant_coefficients=[1],
                            product_types=[bead.type["neutral"], cation.type],
                            product_coefficients=[1,1],
                            default_charges={bead.type["neutral"]: bead.q["neutral"],
                                             bead.type["charged"]: bead.q["charged"],
                                             cation.type: cation.q})
                        reaction_absent[residue.name] = False

                    elif (bead.q["charged"] == -1) : # Acid residue

                        RE.add_reaction(gamma=10**-residue.pKa,
                            reactant_types=[bead.type["neutral"]],
                            reactant_coefficients=[1],
                            product_types=[bead.type["charged"], cation.type],
                            product_coefficients=[1, 1],
                            default_charges={bead.type["neutral"]: bead.q["neutral"],
                                             bead.type["charged"]: bead.q["charged"],
                                             cation.type: cation.q})
                        reaction_absent[residue.name] = False

                    else:
    
                        raise ValueError("This subrutine is concived for the acid/base equilibria of monovalent ions. Charge of residue ", residue.name, " = ", bead.q["charged"])

    return

def calculate_protein_charge(system, protein):
    """ 
    Calculates the charge of the protein and its square

    Inputs:
    system: espresso class object with all system variables
    protein: class object as defined in this library

    Outputs:
    Z_prot: (float) total charge of the protein
    Z2: (float) square of Z_prot
    """
    
    Z_prot=0

    for chain in protein.ids:
        
        for id in chain:

            Z_prot+=system.part[id].q

    Z_prot=Z_prot/protein.N
    Z2=Z_prot**2

    return Z_prot, Z2

def track_ionization(system, protein):
    """
    Sets up espresso to track the average number of particles of each residue type
    
    Inputs:
    system: espresso class object with all system variables
    protein: class object as defined in this library

    """

    types=[]

    for residue in protein.sequence:
        
        for bead in residue.part:

            for type in bead.type.values():

                types.append(type)

    system.setup_type_map(types)

    return

def calculate_HH(pH, protein):
    """
    Calculates the ideal Henderson-Hassebach titration curve in the given pH range

    Inputs:
    pH: (list of floats) list of pH values
    protein: class object as defined in this library

    Outputs:
    Z_HH: (list of floats) Henderson-Hasselnach prediction of the protein charge in the given pH
    """

    Z_HH=[]

    for pH_value in pH:
        
        Z=0

        for residue in protein.sequence:

            if residue.pKa is not None:

                for bead in residue.part:

                    if "charged" in bead.q.keys():

                        Z+=bead.q["charged"]/(1+10**(bead.q["charged"]*(pH_value-residue.pKa)))

        Z_HH.append(Z)

    return Z_HH


def create_counterions(system,protein):
    """
    Adds one monovalent counter-ion (cation or anion) of opposite charge per each charge in the peptide.

    Inputs:

    system: espresso class object with all system variables.
    protein: class object as defined in this library

    Outputs:
    cation/anion: particle class objects of the counter-ions, as defined in this library
        q: (int) charge of the ion
        type: (int) type of the ion

    Assumptions:

    -The charges in system are monovalent
    -The counter-ions are monovalent

    """

    # Load the parameters

    param=parameters()

    # Create and set-up the cation particle object

    cation=particle()
    cation.name="cation"
    cation.q=param.q[cation.name]
    cation.type=param.type[cation.name]
    cation.radi=param.radi[cation.name]
    cation.state="charged"

    # Create and set-up the cation particle object

    anion=particle()
    anion.name="anion"
    anion.q=param.q[anion.name]
    anion.type=param.type[anion.name]
    anion.radi=param.radi[anion.name]
    anion.state="charged"

    # The ids of the counter ions are created to follow the ones of the peptide

    if  len(system.part[:].id) != 0:

        I_id=max(system.part[:].id)

    total_q=0

    # Create a counter-ion for each charged group in the peptide

    cation_id=[]
    anion_id=[]

    for residue in protein.sequence:

        for bead in residue.part:
           
            if bead.state is None:

                raise ValueError("The peptide chains must be created first in the system before creating their counter-ions")

            else:

                for npart in range(bead.N):

                    if bead.q[bead.state] == 1: # Create an anion

                        I_id+=1
                        I_pos=np.random.random((1, 3)) * system.box_l
                        system.part.add(id=[I_id], pos=I_pos, type=[anion.type], q=[anion.q])
                        anion.N+=1
                        anion_id.append(I_id)
                        total_q+=bead.q[bead.state]+anion.q

                    elif bead.q[bead.state] == -1: # Create an anion

                        I_id+=1
                        I_pos=np.random.random((1, 3)) * system.box_l
                        system.part.add(id=[I_id], pos=I_pos, type=[cation.type], q=[cation.q])
                        cation.N+=1
                        cation_id.append(I_id)
                        total_q+=bead.q[bead.state]+cation.q
                    
                    elif bead.q[bead.state] != 0:

                        raise ValueError("This subroutine only considers the case of peptide chains with monovalent charged residues")
    
    cation.ids=cation_id
    anion.ids=anion_id

    if total_q != 0:

        raise ValueError("Subrutine attempted to create a not electroneutral system, please review your peptide set-ups")


    return cation, anion

def generate_trialvectors(mag):
    """
    Generates a random 3D unit vector (direction) with a uniform spherical distribution
    Algorithm from http://stackoverflow.com/questions/5408276/python-uniform-spherical-distribution
    Input:
    
    mag: magnitude of the vector
    
    Output:
    
    vec: random vector of dimension 3
    """

    phi = np.random.uniform(0,np.pi*2)
    costheta = np.random.uniform(-1,1)

    theta = np.arccos( costheta )
    x = np.sin( theta) * np.cos( phi )
    y = np.sin( theta) * np.sin( phi )
    z = np.cos( theta )

    vec=np.array([x,y,z])
    vec=vec*mag

    return vec

def get_subclasses(cls):

    import inspect
    model_list=[]

    for attribute in cls.__dict__.items():

        name_attribute=attribute[0]

        if name_attribute[0:2] != "__" and inspect.isclass(attribute[1]):

            model_list.append(attribute[1])

    return model_list

def get_particles(cls):

    particle_list=[]

    for attribute in cls.__dict__.items():

        if isinstance(attribute[1], param.particle):

            particle_list.append(attribute[1])

    return particle_list

            

def get_attributes(cls):
    import inspect

    attribute_list=[]

    for attribute in  inspect.getmembers(cls, lambda a:not(inspect.isroutine(a))):

        name_attribute=attribute[0]

        if name_attribute[0:2] != "__":

            attribute_list.append(attribute)

    return attribute_list


def newAttr(self, attr):

    setattr(self, attr.name, attr)


def get_modelnames():

    model_names=[]
    model_list=get_subclasses(param)

    for param_set in model_list:

        if param_set.name is not None:
                    
            model_names.append(param_set.name)

    return model_names

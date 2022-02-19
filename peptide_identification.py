import itertools
import pandas as pd


def calc_amino_acid_combinations_based_on_sequence(amino_acid_tuples, complete_amino_acid_dict,
                                                   original_sequence, mass_original_sequence,
                                                   excel_export_path='weight_per_sequence_df_based_on_sequence.xlsx'):
    """

    :param amino_acid_tuples:
    :param complete_amino_acid_dict:
    :param original_sequence:
    :param mass_original_sequence:
    :param excel_export_path:
    :return:
    """

    # get amino acid masses of amino acid sequence to be analyzed and store them as a list (= list_of_mz)
    list_of_mz = []
    for index, tuple in enumerate(amino_acid_tuples):
        list_of_mz.append(tuple[1])

    # get all possible combinations of amino acid residues and store them as a list of tuples (=combinations)
    combinations = [seq for i in range(len(list_of_mz), 0, -1) for seq in
                    itertools.combinations(list_of_mz, i) if sum(seq) <= mass_original_sequence]

    # substitute each mz of in combinations by its corresponding amino acid letter and store it as a list of
    # lists (=list_of_amino_acid_combinations)
    list_of_amino_acid_combinations = []
    for i in range(len(combinations)):
        list_of_amino_acid_combinations.append(
            list(list(complete_amino_acid_dict.keys())
                 [list(complete_amino_acid_dict.values()).index(mz)] for mz in combinations[i]))

    # join the amino acid letter in list_of_amino_acid_combinations and store the result as a list of strings
    # (=list_of_amino_acid_combinations_joined_letters)
    list_of_amino_acid_combinations_joined_letters = []
    for element in range(len(list_of_amino_acid_combinations)):
        joined = ''.join(map(str, list_of_amino_acid_combinations[element]))
        list_of_amino_acid_combinations_joined_letters.append(joined)

    # check whether the strings in list_of_amino_acid_combinations_joined_letters are a component of the original
    # sequence and only store the elements that meet that condition as a list of strings (=el_in_original_sequence)
    el_in_original_sequence = [el for el in list_of_amino_acid_combinations_joined_letters if el in original_sequence]

    # get the corresponding amino acid letter for all elements in el_in_original_sequence and store the result as
    # dictionary (=weight_per_sequence) with the amino acid sequence as key and peptide mass as value
    # transform the dictionary to a dataframe (=weight_per_sequence_df)
    weight_per_sequence = {}
    for sequence in el_in_original_sequence:
        weight_per_sequence.update({sequence: round(sum([complete_amino_acid_dict[amino_acid] for amino_acid in sequence]), 5)})
    weight_per_sequence_df = pd.DataFrame(weight_per_sequence.items(), columns=['sequence', 'mz'])
    weight_per_sequence_df.to_excel(excel_export_path)
    print(f"weight per sequence (based on sequence): \n {weight_per_sequence_df}")
    return weight_per_sequence_df


def calc_amino_acid_combinations_based_on_mz_value(complete_amino_acid_dict, initial_mass, tolerance=0.0,
                                                   excel_export_path='weight_per_sequence_df_based_on_mz.xlsx'):
    # first: substract H2O and H + from parent ion → „initial mass“ for further calculation get all possible
    # combinations of amino acid residues that sum up to the initial mass and store them as a list of tuples
    # ( = combinations)
    combinations = [seq for i in range(len(complete_amino_acid_dict.values()), 0, -1) for seq in
                    itertools.combinations(complete_amino_acid_dict.keys(), i) if
                    initial_mass - tolerance <= sum(map(complete_amino_acid_dict.get, seq)) <= initial_mass + tolerance]

    # get all possible fragments of the amino acid sequences stored in the list of tuples calculated previously
    # ( = combinations).Store the result as a dictionary of lists( = fragment_combinations)
    fragment_combinations = {}
    for element in range(len(combinations)):
        fragments = [combinations[element][i: j] for i in range(len(combinations[element])) for j in
                     range(i + 1, len(combinations[element]) + 1)]
        fragment_combinations.update({element: fragments})

    # get corresponding mass of fragments and store it as a nested dictionary with amino acid sequence as key
    # and corresponding mass as value in lowest level
    weight_per_sequence = {}
    for combination, fragment_list in fragment_combinations.items():
        weight_per_sequence.update({combination: {}})
        for sequence in fragment_list:
            sequence_key = "".join(sequence)
            weight_per_sequence[combination].update({
                sequence_key: sum([complete_amino_acid_dict[amino_acid] for amino_acid in sequence])})

    df_dict = {'variant_id': [], 'sequence': [], 'weights': []}
    for ident, val_dict in weight_per_sequence.items():
        df_dict['variant_id'].extend([ident] * len(val_dict.keys()))
        df_dict['sequence'].extend(list(val_dict.keys()))
        df_dict['weights'].extend(list(val_dict.values()))
    weight_per_sequence_df = pd.DataFrame(df_dict)
    weight_per_sequence_df.to_excel(excel_export_path)
    print(f"weight per sequence (based on mz): \n {weight_per_sequence_df}")
    return weight_per_sequence_df


def main():
    perform_calc_amino_acid_combinations_based_on_sequence = True
    perform_calc_amino_acid_combinations_based_on_mz_value = False

    # Exemplary amino acid sequence stored as a tuple of amino acid letter and corresponding amino acid residue mass
    amino_acid_tuples = [("A", 71.03711), ("V", 99.06841), ("F", 147.06841), ("P", 97.05276), ("S", 87.03203),
                         ("J", 113.08406), ("V", 99.06841), ("G", 57.02146), ("R", 156.10111), ("P", 97.05276),
                         ("R", 156.10111)]

    # dictionary of all amino acid residues stored as tuples of amino acid letter and corresponding amino acid
    # residue mass
    complete_amino_acid_dict = {"A": 71.03711, "R": 156.10111, "N": 114.04293, "D": 115.02694, "C": 103.00919,
                                "E": 129.04259, "Q": 128.05858, "G": 57.02146, "H": 137.05891, "J": 113.08406,
                                "K": 128.09496, "M": 131.04049, "F": 147.06841, "P": 97.05276, "S": 87.03203,
                                "T": 101.04768, "W": 186.07931, "Y": 163.06333, "V": 99.06841}

    original_sequence = "AVFPSJVGRPR"
    mass_original_sequence = 1179.68761
    initial_mass = 850.4528

    if perform_calc_amino_acid_combinations_based_on_sequence:
        calc_amino_acid_combinations_based_on_sequence(amino_acid_tuples, complete_amino_acid_dict,
                                                       original_sequence, mass_original_sequence)

    if perform_calc_amino_acid_combinations_based_on_mz_value:
        calc_amino_acid_combinations_based_on_mz_value(complete_amino_acid_dict, initial_mass, tolerance=0.01)


if __name__ == "__main__":
    main()

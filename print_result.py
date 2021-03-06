from collections import Counter

####
# for other_mwp statistics only
total_data_len = 1557
####

# TODO: > .md in gen, how about segs??

def _print_md_col_names(items):
    ## Print the first 2 lines of a .MarkDown table
    print(f"| {' | '.join([str(item) for item in items])} |")
    print(f"| {' | '.join(['-' for item in items])} |")

def top_templates_from_train(top_temps, temps2sents, metadata, metadata_colnames=[], 
        n_toptemps=5, n_samples=3, filters=None, seg_temps2sents={}, n_examples=2): 
    """
    Parameters:
    ----------
        n_toptemps:   int
            Max number of top templates to print
        n_samples:   int
            Max number of sentence samples to print for each template
        filters:   dict
            Keeps only pure 'Addition', etc. e.g. {'solution type':['Addition']}
    """   
    some_cnames = []
    if metadata_colnames is None and metadata is not None:
        metadata_colnames=list(metadata)
        # HACK If too many catogeries (e.g. 'questions'), don't print its distribution
        some_cnames = [cname for cname in metadata_colnames if len(set(metadata[cname])) < 15]
    overall_stype_counts,solution_types = dict(),dict()
    stype_counts = list()   # [ {'solution type' : {Addition':2, 'Subtraction':1} } ]
    if len(some_cnames) > 0:
        for cname in some_cnames:
            # 'solution type' -> {'Addition':10, 'Subtraction':5}
            overall_stype_counts[cname] = Counter(metadata[cname])

            # 'solution type' -> ['Addition','Subtraction']
            solution_types[cname] = [stype for stype, count in sorted(list(overall_stype_counts[cname].items()), key=lambda x: -x[1])]
    
    
    Ns = 0
    printed = [] # Printed templates' indices in top_temps
    for it, temp in enumerate(top_temps):   # Iterator for Templates
        
        if len(printed) == n_toptemps:      # Iterate only top n_toptemps templates
            break
        sents = temps2sents[temp]
        
        # Check purity
        if filters is not None and metadata is not None:
            pure = True
            for (_, lineno) in sents:
                for (cname, filterlist) in filters.items():
                    if metadata[cname][lineno] not in filterlist:
                        pure = False
                        break
                if not pure:
                    break
            if not pure:
                continue    # Thank u, next template

        N = len(sents)
        Ns += N
        
        if n_samples > 0:
            print(f"### Top-{it+1} ({N} samples using it): {temp}")
            _print_md_col_names([*(temp), *metadata_colnames])#, 'lineno', 'count', 'portion'])

        # Print seg examples
        if seg_temps2sents!={}:
            if temp in seg_temps2sents:
                seg_examples = seg_temps2sents[temp]
                for segi in range(min(n_examples,len(seg_examples))):
                    tokens, lineno = seg_examples[segi]
                    templt = ' | '.join([*tokens, str(lineno)])
                    templt = str(templt.encode('utf-8'))[2:-1]  # HACK ==
                    print(f'| {templt} |')
                print(f'| ')

        # Print gen results
        j = 0
        for (tokens, lineno) in sents:
            if j == n_samples:      # Print only n_samples samples
                break
            attrs = [str(metadata[cname][lineno]) for cname in metadata_colnames] if metadata is not None else []
            templt = ' | '.join([*tokens, *attrs]) #str(lineno),
            templt = str(templt.encode('utf-8'))[2:-1]  # HACK ==
            print(f'| {templt} |')
            j = j + 1
        
        print()
        # Distribution of some metadata_colnames (e.g. solution type) using this template        
        stype_counts.append(dict())
        if len(some_cnames) > 0:
            for cname in some_cnames:
                stype_counts[len(printed)][cname] = Counter([metadata[cname][lineno] for (_, lineno) in sents])
        
        printed.append(it)
    
    # Distribution of some metadata_colnames (e.g. solution type) using this template        
    if len(some_cnames) > 0:
        for cname in some_cnames:
            print(f'### Distribution of {cname}: the {Ns} samples using all top-{n_toptemps} templates')
            _print_md_col_names([' ',*solution_types[cname]])
            for i in range(len(printed)):
                row = f'| top-{printed[i]+1} | '
                N = sum([stype_counts[i][cname][stype] for stype in solution_types[cname]])
                for stype in solution_types[cname]:
                    row += f"{stype_counts[i][cname][stype]} ({stype_counts[i][cname][stype]/N:.3f})" + ' |'
                print(row)
    
    print()
    return printed


def top_template_phrase_examples(top_temps, state2phrases, n_toptemps=5, n_phrases=10):
    """
    Parameters
    -----------
        n_phrases:  int
            Print top {n_phrases} examples for each state
    """
    def _print_it(with_freq):
        for template_it in range(n_toptemps):    # Top 5 templates
            if template_it >= len(top_temps):
                break
            print(f"### Top-{template_it+1}: {top_temps[template_it]}")

            _print_md_col_names(top_temps[template_it])

            template = top_temps[template_it]  # a tuple of states
            template_examples = [[] for i in range(n_phrases)]  #[['phr1-1','phr2-1'], ['ph1-2', 'phr2-2']]
            for i_state,state in enumerate(template):
                # [0] for phrase; [1] for frequency
                phr_frq = sorted(zip(state2phrases[state][1],state2phrases[state][0]), reverse=True)
                for i_exp in range(n_phrases):
                    example_phrase = ' '
                    if i_exp < len(phr_frq):
                        example_phrase = f"{phr_frq[i_exp][1]}"             #e.g. "How much"
                        if with_freq:
                            example_phrase += f" ({phr_frq[i_exp][0]:.2f})"  #e.g. "How much (0.03)"
                    template_examples[i_exp].append(example_phrase)
                    
            for i_exp in range(n_phrases):
                print(f"| {' | '.join(template_examples[i_exp])} |")
            print()

    print(f"# Top {n_toptemps} templates consist of")
    print(f"## No frequencies")
    _print_it(False)
    print(f"## With frequencies")
    _print_it(True)
    


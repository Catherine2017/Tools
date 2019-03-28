import pysam

def read_pattern_judge(read,loc,ref,alt):
    #! 0-based loc stands relative loc of read
    #! loc represent vcf format variant
    #e.g.:
    #    ref:AT  alt:A(M)G(I)C(M)
    #    for the insertion G, loc is 0 and format is A/AG
    #    for the snp C, loc is 1 and format is T/C

    # snp is in M op in bam
    # all uppercase to compare
    seq, ref, alt = read.seq.upper(), ref.upper(), alt.upper()
    ind = 0
    for op, oplen in read.cigar:
        # M:0  I:1  D:2  N:3  S:4  H:5  P:6  =:7  X:8
        ind += 1
        if op == 0 or op == 7 or op == 8:
            if 0<=loc<oplen:
                # find the base loc and judge the pattern from ref/alt

                if len(ref) == len(alt) and loc+len(ref)-1<oplen :
                    # snp   #? suppose X symbol is not use
                    if seq[loc:loc+len(ref)] == alt:
                        return True
                elif len(ref) == 1 and len(alt) >1:
                    # ins
                    if loc==oplen-1 and len(read.cigar)>ind \
                                    and (1, len(alt)-1)==read.cigar[ind]\
                                    and seq[loc] == alt[0]:
                        return True
                elif len(ref) > 1 and len(alt) == 1:
                    # del
                    if loc==oplen-1 and len(read.cigar)>ind \
                                    and (2, len(ref)-1)==read.cigar[ind]\
                                    and seq[loc] == alt[0]:
                        return True
                else:
                    raise ValueError('UnRecognizable Ref/Alt %s %s'%(ref, alt))
                return False

            else:
                seq = seq[oplen:]
                loc -= oplen
        elif op == 1 or op == 4:
            seq = seq[oplen:]
        elif op == 2 or op == 3:
            loc -= oplen
        elif op == 5 or op == 6:
            pass
        else:
            raise ValueError('UnRecognizable Cigar Value ' + str(op))
    return False

The simplices in this dataset correspond to co-sponsorship of bills in the
United States Congress, derived from James Fowler's datasets:
http://jhfowler.ucsd.edu/cosponsorship.htm
Each simplex represents one bill, and the set of vertices is the set consisting
of the sponsor and co-sponsors. Timestamps are in days and represent when
the bill was introduced.

The file congress-bills-names.txt contains the names of the congresspersons.


python prepare_benson_alignment_dataset.py --input-dir ./datasets/simplices/congress-bills --output-dir ./datasets/simplices/congress-bills/congress_bills_hypergraphs --prefix congress-bills --slice-mode event-bin --num-bins 12 --min-size 2 --max-size 25 --pair-scope consecutive --select-pairs 2 --selection-rule first-valid --min-common-nodes 100 --min-common-hyperedges 50 --project-root .
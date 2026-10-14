This dataset is derived from tags on Ask Ubuntu posts. The raw data was
downloaded from
https://archive.org/details/stackexchange

Each simplex corresponds to all of the tags used in a post, and each node in a
simplex corresponds to a tag. The times are the time of the post in millisecond
but normalized so that the earliest tag starts at 0.

The file tags-ask-ubuntu-node-labels.txt maps integer tag ids and the actual tags.

The file tags-ask-ubuntu-simplex-labels.txt contains the post id for each simplex.

python convert_tags_ask_ubuntu_benson_to_hypergraphs.py \
  --input-dir ./ \
  --output-dir ./tags_ask_ubuntu_hypergraphs \
  --slice event-bin \
  --num-bins 12 \
  --min-size 2 \
  --max-size 0 \
  --write-all-pairs \
  --top-k 30 \
  --copy-node-labels
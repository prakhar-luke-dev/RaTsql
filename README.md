# RaTsql : Retrieval-augmented Text-to-SQL

- R: Retrieval
- a: augmented
- Tsql: Text-to-SQL

# Flow dig : [Click to view Flow dig.](https://miro.com/app/board/uXjVJZTBDcc=/?share_link_id=245310762751)

# SETUP : 

## Step 0 : Create env

```bash
conda create -n ratsql python=3.12
conda activate ratsql
```
```bash
pip install -r requirements.txt
```

## Step 1 : Prepare Data

```bash 
python RaTsql/src/modules/prepare_data/prepare_metadata.py
```

## Step 2 : Store data to RAG

```bash
python RaTsql/src/modules/vector_store/populate_vectore_space.py
```

## Step 3 : Run graph
```bash
python RaTsql/src/run_graphs.py
```
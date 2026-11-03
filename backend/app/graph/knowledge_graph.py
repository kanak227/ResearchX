from typing import List, Dict, Any, Optional
import networkx as nx
import re
from ..database.repository import db_repo
from ..core.logging import logger

class ResearchKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph_for_papers(self, paper_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Constructs a NetworkX directed knowledge graph for specified papers or all papers.
        Extracts entities and scientific relationships.
        Returns serialized {nodes: [...], links: [...], stats: {...}}
        """
        self.graph.clear()
        papers = db_repo.list_papers()
        if paper_ids:
            papers = [p for p in papers if p.id in paper_ids]

        if not papers:
            return {"nodes": [], "links": [], "stats": {"total_nodes": 0, "total_edges": 0}}

        logger.info("Constructing Knowledge Graph for %d papers", len(papers))

        # Known entity catalogs for entity recognition
        known_models = ["Transformer", "BERT", "GPT", "ResNet", "LLaMA", "Qwen", "Dense Retrieval", "BM25", "Cross-Encoder", "VLM", "CLIP"]
        known_datasets = ["ImageNet", "GLUE", "SQuAD", "MS MARCO", "MMLU", "arXiv", "PubMed", "HotpotQA", "BEIR"]
        known_metrics = ["Accuracy", "F1-Score", "MRR", "Recall@K", "Precision@K", "Latency", "Perplexity", "ROUGE", "BLEU", "Faithfulness"]

        for paper in papers:
            p_node_id = f"paper_{paper.id}"
            self.graph.add_node(
                p_node_id,
                label=paper.title[:35] + ("..." if len(paper.title) > 35 else ""),
                full_title=paper.title,
                node_type="paper",
                year=paper.published_year or 2024,
                venue=paper.journal_venue or "Conference"
            )

            # Authors
            for author in paper.authors:
                if author and author != "Unknown Authors":
                    a_node_id = f"author_{author.lower().replace(' ', '_')}"
                    if not self.graph.has_node(a_node_id):
                        self.graph.add_node(a_node_id, label=author, node_type="author")
                    self.graph.add_edge(a_node_id, p_node_id, relationship="AUTHORED", weight=1.0)

            # Extract concepts from elements
            elements = db_repo.get_elements_by_paper(paper.id)
            corpus_text = " ".join([e.content for e in elements])
            corpus_lower = corpus_text.lower()

            # Models / Architectures
            for model_name in known_models:
                if model_name.lower() in corpus_lower:
                    m_node_id = f"model_{model_name.lower()}"
                    if not self.graph.has_node(m_node_id):
                        self.graph.add_node(m_node_id, label=model_name, node_type="model")
                    self.graph.add_edge(p_node_id, m_node_id, relationship="USES", weight=1.0)

            # Datasets
            for dataset_name in known_datasets:
                if dataset_name.lower() in corpus_lower:
                    d_node_id = f"dataset_{dataset_name.lower()}"
                    if not self.graph.has_node(d_node_id):
                        self.graph.add_node(d_node_id, label=dataset_name, node_type="dataset")
                    self.graph.add_edge(p_node_id, d_node_id, relationship="EVALUATED_ON", weight=1.0)

            # Metrics
            for metric_name in known_metrics:
                if metric_name.lower() in corpus_lower:
                    met_node_id = f"metric_{metric_name.lower().replace('@', '_').replace('-', '_')}"
                    if not self.graph.has_node(met_node_id):
                        self.graph.add_node(met_node_id, label=metric_name, node_type="metric")
                    self.graph.add_edge(p_node_id, met_node_id, relationship="MEASURES", weight=1.0)

        # Cross-paper comparative edges
        if len(papers) >= 2:
            for i in range(len(papers)):
                for j in range(i + 1, len(papers)):
                    p1_id = f"paper_{papers[i].id}"
                    p2_id = f"paper_{papers[j].id}"
                    # Find shared models or datasets
                    p1_neighbors = set(self.graph.neighbors(p1_id))
                    p2_neighbors = set(self.graph.neighbors(p2_id))
                    shared = p1_neighbors.intersection(p2_neighbors)
                    if shared:
                        self.graph.add_edge(
                            p1_id, p2_id,
                            relationship="COMPARES_WITH",
                            weight=len(shared),
                            shared_entities=list(shared)
                        )

        # Serialize to JSON representation
        nodes = []
        for n_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": n_id,
                "label": attrs.get("label", n_id),
                "type": attrs.get("node_type", "entity"),
                "properties": {k: v for k, v in attrs.items() if k not in ["label", "node_type"]}
            })

        links = []
        for u, v, attrs in self.graph.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "relationship": attrs.get("relationship", "CONNECTED"),
                "weight": attrs.get("weight", 1.0)
            })

        return {
            "nodes": nodes,
            "links": links,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(links),
                "density": round(nx.density(self.graph), 4) if len(nodes) > 1 else 0.0
            }
        }

knowledge_graph = ResearchKnowledgeGraph()


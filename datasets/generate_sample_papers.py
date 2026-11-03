import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io

OUTPUT_DIR = "datasets/sample_papers"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_diagram_image(title: str, blocks: list) -> bytes:
    """Creates a scientific architecture diagram as a PNG."""
    img = Image.new("RGB", (600, 220), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    
    # Outer box
    draw.rectangle([10, 10, 590, 210], outline=(99, 102, 241), width=2)
    draw.text((20, 18), title, fill=(30, 41, 59))

    # Flow blocks
    x = 30
    for idx, (b_title, b_desc) in enumerate(blocks):
        draw.rectangle([x, 60, x + 150, 170], fill=(238, 242, 255), outline=(79, 70, 229), width=2)
        draw.text((x + 10, 75), b_title, fill=(67, 56, 202))
        draw.text((x + 10, 105), b_desc, fill=(71, 85, 105))
        if idx < len(blocks) - 1:
            draw.line([x + 150, 115, x + 180, 115], fill=(79, 70, 229), width=2)
            draw.polygon([(x + 180, 115), (x + 172, 110), (x + 172, 120)], fill=(79, 70, 229))
        x += 180

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def build_paper_1():
    doc = fitz.open()
    
    # Page 1
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 70), "Attention Mechanisms in Deep Neural Architectures: A Comprehensive Empirical Study", fontsize=15, fontname="helv", color=(0.1, 0.1, 0.1))
    p1.insert_text((50, 100), "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    p1.insert_text((50, 120), "Google Brain & Research Labs, 2024. DOI: 10.1145/3345.2024.1102", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    
    abstract_text = (
        "Abstract—Dominant sequence transduction models are based on complex recurrent or convolutional neural networks "
        "that include an encoder and a decoder. In this work, we evaluate the Transformer, a model architecture eschewing recurrence "
        "and instead relying entirely on an attention mechanism to draw global dependencies between input and output. "
        "Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable "
        "and requiring significantly less time to train."
    )
    p1.insert_textbox(fitz.Rect(50, 140, 545, 220), abstract_text, fontsize=9.5, fontname="times-roman")

    sec1_text = (
        "1. Introduction\n"
        "Recurrent neural networks, long short-term memory (LSTM) and gated recurrent neural networks have been firmly established "
        "as state-of-the-art approaches in sequence modeling. Recurrent models typically factor computation along the symbol positions "
        "of the input and output sequences. This inherently sequential nature precludes parallelization within training examples, which "
        "becomes critical at longer sequence lengths, as memory constraints limit batching across examples.\n\n"
        "2. Model Architecture\n"
        "The Transformer follows an overall architecture using stacked self-attention and point-wise, fully connected layers for both the "
        "encoder and decoder. The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a "
        "multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network."
    )
    p1.insert_textbox(fitz.Rect(50, 230, 545, 450), sec1_text, fontsize=9.5, fontname="times-roman")

    # Insert Figure 1 on page 1
    fig_bytes = create_diagram_image(
        "Figure 1: Transformer Stacked Encoder-Decoder Architecture",
        [("Input Embed", "Positional Enc"), ("Multi-Head", "Self-Attention"), ("Feed Forward", "Residual Add")]
    )
    p1.insert_image(fitz.Rect(50, 470, 545, 620), stream=fig_bytes)
    p1.insert_text((50, 635), "Figure 1: The Transformer model architecture utilizing stacked multi-head self-attention and layer normalization.", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))

    eq_text = (
        "3. Scaled Dot-Product Attention\n"
        "We compute the attention function on a set of queries simultaneously, packed together into a matrix Q. "
        "The keys and values are also packed into matrices K and V:\n\n"
        "Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V    (1)\n\n"
        "where d_k is the dimension of the keys and queries. Scaling prevents softmax saturation in high-dimensional spaces."
    )
    p1.insert_textbox(fitz.Rect(50, 655, 545, 780), eq_text, fontsize=9.5, fontname="times-roman")

    # Page 2
    p2 = doc.new_page(width=595, height=842)
    sec4_text = (
        "4. Experimental Evaluation & Results\n"
        "On the WMT 2014 English-to-German translation task, the big transformer model achieves a BLEU score of 28.4. "
        "On the WMT 2014 English-to-French translation task, our model establishes a new state-of-the-art score of 41.8 BLEU.\n"
        "Table 1 outlines performance benchmarks compared with recurrent and convolutional architectures."
    )
    p2.insert_textbox(fitz.Rect(50, 60, 545, 140), sec4_text, fontsize=9.5, fontname="times-roman")

    # Table 1
    tab1_text = (
        "Table 1: Translation Benchmark on WMT 2014 English-to-German and English-to-French\n"
        "| Architecture | En-De BLEU | En-Fr BLEU | Training FLOPs | Latency (ms) |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| ByteNet | 23.75 | 39.20 | 1.0e19 | 145 |\n"
        "| ConvS2S | 25.16 | 40.46 | 9.6e18 | 120 |\n"
        "| MoE | 26.03 | 40.56 | 2.0e19 | 180 |\n"
        "| Transformer (Base) | 27.30 | 38.10 | 3.3e18 | 48 |\n"
        "| Transformer (Big) | 28.40 | 41.80 | 2.3e19 | 82 |\n"
    )
    p2.insert_textbox(fitz.Rect(50, 150, 545, 300), tab1_text, fontsize=9, fontname="courier")

    sec5_text = (
        "5. Computational Complexity Analysis\n"
        "The computational complexity per layer of Self-Attention is O(n^2 * d), where n is the sequence length and d is representation dimension.\n"
        "In contrast, Recurrent layers require O(n * d^2) operations with O(n) sequential operations.\n\n"
        "6. Stated Limitations\n"
        "The primary limitation noted by the authors is the quadratic computational complexity with respect to sequence length n. "
        "For very long documents (n > 4096), GPU memory consumption grows quadratically. Additionally, the model lacks an innate "
        "concept of recurrent order, necessitating positional encodings.\n\n"
        "7. Future Work & Conclusion\n"
        "Future research directions include extending attention mechanisms to handle multimodal inputs such as imagery, audio, and video, "
        "as well as investigating sparse attention approximations to lower memory footprint."
    )
    p2.insert_textbox(fitz.Rect(50, 310, 545, 600), sec5_text, fontsize=9.5, fontname="times-roman")

    doc.save(os.path.join(OUTPUT_DIR, "Paper1_Transformer_Attention_Mechanisms.pdf"))
    doc.close()
    print("Created Paper 1: Transformer_Attention_Mechanisms.pdf")

def build_paper_2():
    doc = fitz.open()
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 70), "Multimodal Retrieval-Augmented Generation for Scientific Literature Intelligence", fontsize=15, fontname="helv", color=(0.1, 0.1, 0.1))
    p1.insert_text((50, 100), "Patrick Lewis, Ethan Perez, Aleksandra Piktus, Sebastian Riedel", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    p1.insert_text((50, 120), "Meta AI Research & University College London, 2024. DOI: 10.1145/3678.2024.0891", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    abstract_text = (
        "Abstract—Large language models often struggle to synthesize information accurately from complex technical papers containing "
        "tables, architecture diagrams, and mathematical formulations. We propose Multimodal-RAG, an architecture combining dense vector "
        "embeddings, BM25 inverted keyword indices, and structured extraction of figures and tables. Evaluations demonstrate that "
        "incorporating multimodal elements improves Mean Reciprocal Rank (MRR) by 26.4% and citation accuracy by 34.2% over text-only baselines."
    )
    p1.insert_textbox(fitz.Rect(50, 140, 545, 230), abstract_text, fontsize=9.5, fontname="times-roman")

    sec1_text = (
        "1. Introduction & Problem Statement\n"
        "Scientific literature is inherently multimodal: vital findings, performance metrics, and model layouts reside inside tables "
        "and figures rather than body paragraphs. Conventional text-only RAG systems discard non-textual data during document ingestion, "
        "yielding hallucinated responses when querying numerical metrics or architecture workflows.\n\n"
        "2. Proposed Hybrid Multimodal Retrieval Pipeline\n"
        "Our method introduces a unified indexing pipeline. PDFs are parsed into structural text, markdown tables, high-resolution figures, "
        "and mathematical equations. Retrieval combines dense vector search with sparse BM25 scoring using Reciprocal Rank Fusion (RRF):\n\n"
        "RRF_Score(d) = sum(w_i / (k + rank_i(d)))    (1)\n\n"
        "where k = 60 and w_i is the modality weight parameter."
    )
    p1.insert_textbox(fitz.Rect(50, 240, 545, 470), sec1_text, fontsize=9.5, fontname="times-roman")

    fig_bytes = create_diagram_image(
        "Figure 1: Multimodal Ingestion and Verification Flowchart",
        [("PDF Ingest", "Table / Fig"), ("Hybrid Index", "Dense + BM25"), ("Reranker", "Claim Verifier")]
    )
    p1.insert_image(fitz.Rect(50, 480, 545, 630), stream=fig_bytes)
    p1.insert_text((50, 645), "Figure 1: Multimodal RAG pipeline integrating structural PDF parsing, hybrid search, and deterministic claim verification.", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))

    # Page 2
    p2 = doc.new_page(width=595, height=842)
    sec3_text = (
        "3. Experimental Benchmarks\n"
        "We evaluate on the SciDoc-QA benchmark across 30 research papers. We compare four configurations: "
        "Text-Only RAG, Hybrid Text RAG, Multimodal RAG, and Multimodal RAG with Cross-Encoder Reranking."
    )
    p2.insert_textbox(fitz.Rect(50, 60, 545, 120), sec3_text, fontsize=9.5, fontname="times-roman")

    tab1_text = (
        "Table 1: Retrieval and Grounding Performance across Scientific RAG Configurations\n"
        "| Configuration | Precision@5 | Recall@5 | MRR | Citation Acc (%) | Faithfulness (%) |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| Exp A: Text-Only RAG | 0.520 | 0.610 | 0.540 | 58.2 | 64.5 |\n"
        "| Exp B: Hybrid Text RAG | 0.640 | 0.720 | 0.670 | 71.0 | 73.2 |\n"
        "| Exp C: Multimodal RAG | 0.780 | 0.850 | 0.810 | 84.6 | 82.0 |\n"
        "| Exp D: Multimodal + Rerank | 0.890 | 0.940 | 0.910 | 94.2 | 91.8 |\n"
    )
    p2.insert_textbox(fitz.Rect(50, 130, 545, 270), tab1_text, fontsize=9, fontname="courier")

    sec4_text = (
        "4. Stated Limitations & Hardware Bottlenecks\n"
        "The authors explicitly state that extracting vector diagrams and rasterizing complex mathematical equations "
        "introduces a 15-20% latency overhead during initial PDF ingestion. Furthermore, vision-language models required "
        "for dense diagram captioning require substantial GPU VRAM, presenting deployment hurdles on edge and CPU-only devices.\n\n"
        "5. Future Work\n"
        "We plan to investigate lightweight heuristic diagram classification combined with ONNX-quantized cross-encoders "
        "to deliver real-time sub-second query latency on commodity hardware."
    )
    p2.insert_textbox(fitz.Rect(50, 280, 545, 500), sec4_text, fontsize=9.5, fontname="times-roman")

    doc.save(os.path.join(OUTPUT_DIR, "Paper2_Multimodal_Retrieval_Augmented_Generation.pdf"))
    doc.close()
    print("Created Paper 2: Multimodal_Retrieval_Augmented_Generation.pdf")

def build_paper_3():
    doc = fitz.open()
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 70), "Deterministic Evidence Verification in Parameter-Constrained Local LLMs", fontsize=15, fontname="helv", color=(0.1, 0.1, 0.1))
    p1.insert_text((50, 100), "James Thorne, Andreas Vlachos, Christos Christodoulopoulos", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    p1.insert_text((50, 120), "University of Cambridge & Amazon Research, 2024. DOI: 10.1145/3812.2024.0415", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    abstract_text = (
        "Abstract—Hallucination rates in small language models (1B to 3B parameters) remain high when performing extractive "
        "scientific synthesis. We propose a deterministic evidence verification layer that breaks generated responses into atomic factual "
        "claims and validates n-gram overlap, numerical values, and bounding-box coordinates against retrieved source passages. "
        "Empirical trials show hallucinated citations drop by 78.4% without requiring expensive model fine-tuning."
    )
    p1.insert_textbox(fitz.Rect(50, 140, 545, 230), abstract_text, fontsize=9.5, fontname="times-roman")

    sec1_text = (
        "1. Introduction & Methodology\n"
        "When local open-weight models such as LLaMA-3.2 (1B/3B) or Qwen-2.5 (1.5B) run on consumer CPUs, their generation cannot "
        "be assumed mathematically sound. In high-stakes research intelligence, asserting an unverified claim can compromise scientific integrity.\n\n"
        "2. Deterministic Claim Decomposition & Alignment\n"
        "Our verification layer operates in three discrete stages:\n"
        "1. Atomic claim decomposition: Answer strings are partitioned into verifiable propositions.\n"
        "2. Lexical and numeric alignment: Exact matching of reported metric percentages (e.g., 94.2%) and keyword n-grams.\n"
        "3. Confidence calibration: A deterministic score between 0.0 and 1.0 is computed without LLM prompt fabrication:\n\n"
        "Score(c, E) = 0.7 * Overlap(c, E) + 0.3 * NumberMatch(c, E)    (1)\n"
    )
    p1.insert_textbox(fitz.Rect(50, 240, 545, 480), sec1_text, fontsize=9.5, fontname="times-roman")

    fig_bytes = create_diagram_image(
        "Figure 1: Claim Verification and Citation Scoring Architecture",
        [("Generated Ans", "Sentence Split"), ("Evidence Align", "Token Overlap"), ("Verified Tag", "Page Provenance")]
    )
    p1.insert_image(fitz.Rect(50, 490, 545, 640), stream=fig_bytes)
    p1.insert_text((50, 655), "Figure 1: Three-tier deterministic claim verification pipeline linking assertions to primary page coordinates.", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))

    # Page 2
    p2 = doc.new_page(width=595, height=842)
    sec3_text = (
        "3. Experimental Findings\n"
        "We tested the verification layer across 150 technical scientific questions. "
        "Table 1 highlights hallucination reduction and citation accuracy across parameter scales."
    )
    p2.insert_textbox(fitz.Rect(50, 60, 545, 120), sec3_text, fontsize=9.5, fontname="times-roman")

    tab1_text = (
        "Table 1: Citation Accuracy and Hallucination Rates With and Without Verification\n"
        "| Model Scale | Verification | Citation Acc (%) | Hallucination Rate (%) | Latency (s) |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| LLaMA-3.2 (1B) | Off | 52.4 | 38.6 | 1.85 |\n"
        "| LLaMA-3.2 (1B) | On | 88.5 | 6.2 | 1.98 |\n"
        "| LLaMA-3.2 (3B) | Off | 64.1 | 29.4 | 3.40 |\n"
        "| LLaMA-3.2 (3B) | On | 94.8 | 4.1 | 3.55 |\n"
        "| Qwen-2.5 (1.5B)| On | 91.2 | 5.4 | 2.15 |\n"
    )
    p2.insert_textbox(fitz.Rect(50, 130, 545, 270), tab1_text, fontsize=9, fontname="courier")

    sec4_text = (
        "4. Stated Limitations\n"
        "The authors note that purely lexical and n-gram overlap can occasionally misclassify valid high-level abstract paraphrases "
        "as partially supported rather than fully verified. A hybrid syntactic dependency parser could mitigate this in future iterations.\n\n"
        "5. Conclusion\n"
        "Deterministic post-hoc verification provides a reliable, transparent safeguard against hallucinated citations, enabling safe deployment "
        "of lightweight local models in scientific research workflows."
    )
    p2.insert_textbox(fitz.Rect(50, 280, 545, 480), sec4_text, fontsize=9.5, fontname="times-roman")

    doc.save(os.path.join(OUTPUT_DIR, "Paper3_Evidence_Grounded_Fact_Verification.pdf"))
    doc.close()
    print("Created Paper 3: Evidence_Grounded_Fact_Verification.pdf")

if __name__ == "__main__":
    build_paper_1()
    build_paper_2()
    build_paper_3()
    print("All 3 sample research papers generated successfully in datasets/sample_papers/")


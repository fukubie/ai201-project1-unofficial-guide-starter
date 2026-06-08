# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system is an AI advisor that helps students learn about Computer Science professors at North Carolina A&T State University (NCAT). It brings together information about what professors teach, what they research, and what students say about their classes.

**Why this matters:** The official NCAT website only shows basic information like email addresses and degrees. It doesn't tell you if a professor grades hard, cancels class often, uses old recorded videos, or teaches in a way you like. Students have to ask other students or guess. This system puts all that scattered information in one place so students can make smart choices about which professors to take classes from and which professors to ask for research help.

**Where the information comes from:** We collected detailed files about 15 Computer Science professors that include their teaching history, research papers, student reviews, and office locations.

---

## Document Sources

We collected 15 detailed text files about NCAT Computer Science professors. Each file includes their teaching history, research interests, student reviews, office location, and active projects.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Dr. Kaushik Roy | Faculty Profile | `documents/prof_kaushik_roy.txt` |
| 2 | Dr. Kelvin Bryant | Faculty Profile | `documents/prof_kelvin_bryant.txt` |
| 3 | Dr. Xiaohong Yuan | Faculty Profile | `documents/prof_xiaohong_yuan.txt` |
| 4 | Dr. Huiming Yu | Faculty Profile | `documents/prof_huiming_yu.txt` |
| 5 | Dr. Sajad Khorsandroo | Faculty Profile | `documents/prof_sajad_khorsandroo.txt` |
| 6 | Dr. Jinsheng Xu | Faculty Profile | `documents/prof_jinsheng_xu.txt` |
| 7 | Dr. Mahmoud Abdelsalam | Faculty Profile | `documents/prof_mahmoud_abdelsalam.txt` |
| 8 | Dr. Hamidreza Moradi | Faculty Profile | `documents/prof_hamidreza_moradi.txt` |
| 9 | Dr. Olusola Odeyomi | Faculty Profile | `documents/prof_olusola_odeyomi.txt` |
| 10 | Dr. Letu Qingge | Faculty Profile | `documents/prof_letu_qingge.txt` |
| 11 | Dr. Madhuri Siddula | Faculty Profile | `documents/prof_madhuri_siddula.txt` |
| 12 | Dr. Shaohu Zhang | Faculty Profile | `documents/prof_shaohu_zhang.txt` |
| 13 | Dr. Tony Gwyn | Faculty Profile | `documents/prof_tony_gwyn.txt` |
| 14 | Dr. Shondale Rhodes | Faculty Profile | `documents/prof_shondale_rhodes.txt` |
| 15 | Dr. Brian Scavotto | Faculty Profile | `documents/prof_brian_scavotto.txt` |

---

## Chunking Strategy

We split each professor's file into smaller pieces called "chunks" that the AI can process one at a time.

**Chunk size:** 500 characters (about 125 words each)

**Overlap:** 50 characters between chunks

**Why these choices fit your documents:**
- We started with 1,000 character chunks, but that was too big. When information about different topics (like teaching and research) got mixed in one chunk, the AI search couldn't tell which professor it should return.
- Reducing to 500 characters keeps each chunk focused on one topic (like "office location" or "research interests").
- The 50-character overlap makes sure information at chunk boundaries doesn't get lost — if a sentence starts at the end of one chunk, it also appears at the start of the next.
- We cleaned up the text before chunking by removing extra blank lines and HTML codes.

**Final chunk count:** 207 total chunks across all 15 professor files

---

## Embedding Model

**Model used:** BAAI/bge-large-en-v1.5 (from Sentence Transformers)

**Why we chose this model:** An "embedding model" turns text into numbers that the AI can use to find similar text. We started with a smaller, faster model (`all-MiniLM-L6-v2`), but it wasn't accurate enough — when students asked "Where is Dr. Tony Gwyn's office?" it was returning other professors' office locations because the small model couldn't tell professors apart. We switched to BGE-Large, a much stronger model with 330 million parameters (vs. 22 million for the small one). It's much better at understanding which professor a question is about. Test results jumped from 66% accuracy to 100%.

**Production tradeoff reflection:** If cost wasn't a problem and this system had real users, we'd keep using BGE-Large because accuracy matters most for student decision-making. The main tradeoff is speed — it takes about 2-3 times longer to search than the smaller model. But with our RTX 5060 GPU and 32GB RAM, response time is still fast enough for students. For a very large system with thousands of daily users, we might consider a hybrid approach: use BGE-Large to rank the top results and a faster model for initial filtering. For multilingual universities, we could try the multilingual version of BGE that supports 100+ languages.

---

## Grounded Generation

"Grounding" means the AI only answers based on the professor information we gave it — it doesn't make up facts.

**System prompt grounding instruction:**
We gave the AI a clear system message with five rules:
1. "Answer ONLY using the provided context blocks below."
2. "If the context does not contain the answer, state clearly: 'I don't have information about this in my knowledge base.'"
3. "Never guess, assume, or hallucinate professor data — stick to what's provided."
4. "Always cite which professor the information came from when relevant."
5. "Be conversational and friendly, but accurate and concise."

The system prompt also lists what information the AI has access to (teaching history, research, reviews, office locations, research areas) so the AI knows what it *can* answer about.

**How source attribution is surfaced in the response:**
When we retrieve context chunks, we format them with the professor's name attached. For example: `[Source 1 - Dr. Xiaohong Yuan]` followed by the actual text. The AI sees this format and naturally mentions the professor's name in its answer. We also tell the AI to "cite which professor the information came from" in the system prompt, so it links facts directly to people: "Dr. Xiaohong Yuan published..." rather than "It was published..."

**Why this works:** By combining a clear instruction + source-labeled context + the constraint that the AI only sees limited information, we make it very hard for the AI to hallucinate. If a student asks about a professor we don't have data for, the AI will say "I don't have information about that professor" instead of making something up.

---

## Evaluation Report

Use the 5 test questions from `planning.md` to test your system. Run each question through the Gradio chat interface (`python app.py`), record what the system returns, and compare it to the expected answer.

**Test questions from planning.md:**
1. What did Dr. Xiaohong Yuan publish in 2024 regarding network security education?
2. Where is Dr. Tony Gwyn Primary Office Location?
3. What courses did Dr. Letu Qingge teach?
4. What is Dr. Kelvin Bryant active research?
5. What percentage of students would take professor huiming yu again?

| # | Question | Expected Answer | System Response (Summarized) | Retrieval Quality | Response Accuracy |
| :-: | :--- | :--- | :--- | :-: | :-: |
| **1** | What did Dr. Xiaohong Yuan publish in 2024 regarding network security education? | "Using Gamification to Enhance Mastery of Network Security Concepts" | Dr. Xiaohong Yuan published "Using Gamification to Enhance Mastery of Network Security Concepts" | Relevant | Accurate |
| **2** | Where is Dr. Tony Gwyn Primary Office Location? | Mcnair Hall | Mr. Tony Gwyn's office is located in McNair Hall. | Relevant | Accurate |
| **3** | What courses did Dr. Letu Qingge teach? | COMP 267: Data Base Design<br>COMP 285: Analysis of Algorithms<br>COMP 385: Theory of Computing<br>COMP 496: Senior Project II<br>COMP 790: Independent Study | COMP 267: Data Base Design<br>COMP 285: Analysis of Algorithms<br>COMP 385: Theory of Computing<br>COMP 496: Senior Project II<br>COMP 790: Independent Study | Relevant | Accurate |
| **4** | What is Dr. Kelvin Bryant active research? | Computer science education tracking, introductory student programming support, gamified network security instructional loops, typed-chat text analytics, and touch dynamics authentication schemes using Support Vector Machines (SVM). | Computer science education, introductory student programming support, gamified network security instructional loops, typed-chat text analytics, and touch dynamics authentication schemes using Support Vector Machines | Relevant | Accurate |
| **5** | What percentage of students would take professor huiming yu again? | 0% | 0% | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

During our test phase (Milestone 4), we found one case that failed with our first setup:

**Question that failed:** "Where is Dr. Tony Gwyn's office located?"

**What the system returned:** It returned "McNair Hall" but ranked the wrong professor (Olusola Odeyomi) first instead of Tony Gwyn first, even though McNair Hall was the correct answer.

**Root cause (tied to a specific pipeline stage):** The embedding model stage. We were using `all-MiniLM-L6-v2`, a small embedding model (22 million parameters). When multiple professors work in the same location (McNair Hall), the model couldn't tell them apart — it returned all McNair Hall mentions as equally relevant. The model didn't have enough "understanding" to link the professor's name to their office location. It treated the question like a simple keyword match instead of understanding that we were asking specifically about Tony Gwyn.

**What you would change to fix it:** We upgraded the embedding model from `all-MiniLM-L6-v2` (22M params) to `BAAI/bge-large-en-v1.5` (330M params). This stronger model has much better "entity awareness" — it understands that "Dr. Tony Gwyn" and "McNair Hall" in the same context go together. We also reduced chunk size from 1,000 to 500 characters so each chunk focuses on one topic instead of mixing information. After these changes, the same question returned Tony Gwyn's office first with 100% accuracy.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The Chunking Strategy and Retrieval Approach sections in `planning.md` were like a roadmap. I started with the exact chunk sizes and embedding model they recommended (`all-MiniLM-L6-v2`, 1,000 characters). When the initial tests showed weak accuracy, I had specific metrics to compare against — I could see that distance scores were 0.43-0.73 (bad) instead of where they should be. Because the spec was concrete, I could measure what wasn't working and make targeted improvements instead of guessing. I upgraded the embedding model and measured the distance scores again — they dropped to 0.20-0.45 (good). The spec gave me a way to validate my changes were actually better.

**One way your implementation diverged from the spec, and why:**
The spec recommended 1,000-character chunks with 150-character overlap. We ended up using 500-character chunks with 50-character overlap. This divergence happened because the 1,000-character chunks were mixing multiple topics together (teaching history + research + reviews all in one chunk). When the embedding model tried to find relevant information, it got confused because each chunk was too broad. The smaller chunks (500 chars) keep each topic focused and tight, which made the embedding model much better at finding exactly what students asked about. The spec was a starting point, but real-world testing showed that smaller, focused chunks worked better for this domain.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I gave Claude my vector search results from Milestone 4 because my search query for "Dr. Tony Gwyn's office" was pulling up the wrong professor's office instead.
- *What it produced:* Claude suggested fixing the issue by adding a complex "re-ranker" system or switching my embedding models.
- *What I changed or overrode:* I rejected the idea of adding a complicated re-ranker. Instead, I directed the AI to upgrade my embedding model to `BAAI/bge-large-en-v1.5` and change my text chunk size to 500 characters so the data would be denser. This boosted my search accuracy to 100%.

**Instance 2**

- *What I gave the AI:* I gave Claude my final architecture plan and asked it to write the `app.py` script using the Groq API and Gradio for the user interface.
- *What it produced:* It wrote the script, but it kept guessing the wrong Groq model names (like `gemma2-9b-it`) which caused API errors. It also added a `theme=gr.themes.Soft()` setting to the Gradio code that crashed my app due to versioning. 
- *What I changed or overrode:* I stopped the AI from hallucinating model names and forced it to hardcode the exact correct model: `llama-3.1-8b-instant`. I also manually went into the Python code and deleted the `theme` line so the web interface could launch without throwing a TypeError.

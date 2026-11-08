[2601.02780] MiMo-V2-Flash Technical Report
Skip to main content
Search
Submit
Donate
Log in
Search arXiv
Press Enter to search · Advanced search
Computer Science > Computation and Language
arXiv:2601.02780 (cs)
[Submitted on 6 Jan 2026 (v1), last revised 8 Jan 2026 (this version, v2)]
Title:MiMo-V2-Flash Technical Report
Authors:Xiaomi LLM-Core Team: Bangjun Xiao, Bingquan Xia, Bo Yang, Bofei Gao, Bowen Shen, Chen Zhang, Chenhong He, Chiheng Lou, Fuli Luo, Gang Wang, Gang Xie, Hailin Zhang, Hanglong Lv, Hanyu Li, Heyu Chen, Hongshen Xu, Houbin Zhang, Huaqiu Liu, Jiangshan Duo, Jianyu Wei, Jiebao Xiao, Jinhao Dong, Jun Shi, Junhao Hu, Kainan Bao, Kang Zhou, Lei Li, Liang Zhao, Linghao Zhang, Peidian Li, Qianli Chen, Shaohui Liu, Shihua Yu, Shijie Cao, Shimao Chen, Shouqiu Yu, Shuo Liu, Tianling Zhou, Weijiang Su, Weikun Wang, Wenhan Ma, Xiangwei Deng, Bohan Mao, Bowen Ye, Can Cai, Chenghua Wang, Chengxuan Zhu, Chong Ma, Chun Chen, Chunan Li, Dawei Zhu, Deshan Xiao, Dong Zhang, Duo Zhang, Fangyue Liu, Feiyu Yang, Fengyuan Shi, Guoan Wang, Hao Tian, Hao Wu, Heng Qu, Hongfei Yi, Hongxu An, Hongyi Guan, Xing Zhang, Yifan Song, Yihan Yan, Yihao Zhao, Yingchun Lai, Yizhao Gao, Yu Cheng, Yuanyuan Tian, Yudong Wang, Zhen Tang, Zhengju Tang, Zhengtao Wen, Zhichao Song, Zhixian Zheng, Zihan Jiang, Jian Wen, Jiarui Sun, Jiawei Li, Jinlong Xue, Jun Xia, Kai Fang, Menghang Zhu, Nuo Chen, Qian Tu, Qihao Zhang, Qiying Wang, Rang Li, Rui Ma, Shaolei Zhang, Shengfan Wang, Shicheng Li, Shuhao Gu, Shuhuai Ren, Sirui Deng, Tao Guo
, Tianyang Lu, Weiji Zhuang, Weikang Zhang, Weimin Xiong, Wenshan Huang, Wenyu Yang, Xin Zhang, Xing Yong, Xu Wang, Xueyang Xie, Yilin Jiang, Yixin Yang, Yongzhe He, Yu Tu, Yuanliang Dong, Yuchen Liu, Yue Ma, Yue Yu, Yuxing Xiang, Zhaojun Huang, Zhenru Lin, Zhipeng Xu, Zhiyang Chen, Zhonghua Deng, Zihan Zhang, Zihao Yue
et al. (26 additional authors not shown)
You must enable JavaScript to view entire author list.
View a PDF of the paper titled MiMo-V2-Flash Technical Report, by Xiaomi LLM-Core Team: Bangjun Xiao and 124 other authors
View PDF
HTML (experimental)
Abstract:We present MiMo-V2-Flash, a Mixture-of-Experts (MoE) model with 309B total parameters and 15B active parameters, designed for fast, strong reasoning and agentic capabilities. MiMo-V2-Flash adopts a hybrid attention architecture that interleaves Sliding Window Attention (SWA) with global attention, with a 128-token sliding window under a 5:1 hybrid ratio. The model is pre-trained on 27 trillion tokens with Multi-Token Prediction (MTP), employing a native 32k context length and subsequently extended to 256k. To efficiently scale post-training compute, MiMo-V2-Flash introduces a novel Multi-Teacher On-Policy Distillation (MOPD) paradigm. In this framework, domain-specialized teachers (e.g., trained via large-scale reinforcement learning) provide dense and token-level reward, enabling the student model to perfectly master teacher expertise. MiMo-V2-Flash rivals top-tier open-weight models such as DeepSeek-V3.2 and Kimi-K2, despite using only 1/2 and 1/3 of their total parameters, respectively. During inference, by repurposing MTP as a draft model for speculative decoding, MiMo-V2-Flash achieves up to 3.6 acceptance length and 2.6x decoding speedup with three MTP layers. We open-source both the model weights and the three-layer MTP weights to foster open research and community collaboration.
Comments:
31 pages, technical report
Subjects:
Computation and Language (cs.CL); Artificial Intelligence (cs.AI)
Cite as:
arXiv:2601.02780 [cs.CL]
(or
arXiv:2601.02780v2 [cs.CL] for this version)
https://doi.org/10.48550/arXiv.2601.02780
Focus to learn more
arXiv-issued DOI via DataCite
Submission history From: Shijie Cao [view email]
[v1]
Tue, 6 Jan 2026 07:31:47 UTC (314 KB)
[v2]
Thu, 8 Jan 2026 05:52:17 UTC (314 KB)
Full-text links:
Access Paper:
View a PDF of the paper titled MiMo-V2-Flash Technical Report, by Xiaomi LLM-Core Team: Bangjun Xiao and 124 other authors
View PDF
HTML (experimental)
TeX Source
view license
Additional Features
Audio Summary
Current browse context:
cs.CL
< prev
|
next >
new
|
recent
| 2026-01
Change to browse by:
cs
cs.AI
References & Citations
SciX
Google Scholar
Semantic Scholar
export BibTeX citation
Loading...
BibTeX formatted citation
×
loading...
Data provided by:
Bookmark
Bibliographic Tools
Bibliographic and Citation Tools
Bibliographic Explorer Toggle
Bibliographic Explorer (What is the Explorer?)
Connected Papers Toggle
Connected Papers (What is Connected Papers?)
Litmaps Toggle
Litmaps (What is Litmaps?)
scite.ai Toggle
scite Smart Citations (What are Smart Citations?)
Code, Data, Media
Code, Data and Media Associated with this Article
alphaXiv Toggle
alphaXiv (What is alphaXiv?)
Links to Code Toggle
CatalyzeX Code Finder for Papers (What is CatalyzeX?)
DagsHub Toggle
DagsHub (What is DagsHub?)
GotitPub Toggle
Gotit.pub (What is GotitPub?)
Huggingface Toggle
Hugging Face (What is Huggingface?)
ScienceCast Toggle
ScienceCast (What is ScienceCast?)
Demos
Demos
Replicate Toggle
Replicate (What is Replicate?)
Spaces Toggle
Hugging Face Spaces (What is Spaces?)
Spaces Toggle
TXYZ.AI (What is TXYZ.AI?)
Related Papers
Recommenders and Search Tools
Link to Influence Flower
Influence Flower (What are Influence Flowers?)
Core recommender toggle
CORE Recommender (What is CORE?)
Author
Venue
Institution
Topic
About arXivLabs
arXivLabs: experimental projects with community collaborators
arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.
Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.
Which authors of this paper are endorsers? |
Disable MathJax (What is MathJax?)
We gratefully acknowledge support from our major funders,
member institutions, ,
and all contributors.
About ·
Help ·
Contact ·
Subscribe ·
Copyright ·
Privacy ·
Accessibility ·
Operational Status (opens in new tab)
Major funding support from
(opens in new tab)
(opens in new tab)
(opens in new tab)
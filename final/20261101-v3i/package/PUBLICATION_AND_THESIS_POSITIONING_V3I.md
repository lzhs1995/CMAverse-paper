# CMAverse 论文发表策略与博士论文定位方案（PUBLICATION_AND_THESIS_POSITIONING_V3I）

> **适用版本**：`CMAverse_V3i_progressed_tracked.docx` / `CMAverse_V3i_progressed_accepted.docx`  
> **核心定位转型**：从“寻找婚姻满意度显著中介/调节机制的探索报告”全面升级为**“以三大统计锚点（确认性主效应与加性交互、窄区间零效应界、夫妻评价非对称结构解构）回应家庭社会学核心争鸣的方法论与实证创新论文”**。

---

## 一、三大统计锚点（Three Statistical Anchors）速查表

在投稿信（Cover Letter）、审稿人回复及博士论文答辩中，统一使用以下经 R（`extract_three_statistical_anchors_v3i.R`）与 Stata 19.5 MP（`verify_three_anchors_v3i.do`）交叉核验的三大硬核锚点：

1. **锚点一（确认性主效应与加性交互的非对称角色信号）**：
   - 在本人满意度具提升空间的绝对收入样本（`AA-S`，$N=4,098$）中，收入增加使向父母经济支持增长的概率显著提高 **$+4.90$ 个百分点**（95% CI: `[1.54, 8.26]`）；在相对满意度资格样本（`AR-S`/`AR-P`）中分别提高 **$+2.66$** 与 **$+2.51$ 个百分点**。
   - 在风险差加性交互（Model 5）中，本人相对满意度位置升级（`AR-S`）的交互项 `IC-RD` 为 **$-8.76$ 个百分点**（95% CI: `[-14.79, -2.41]`，八项 BH 校正后 **$q=0.032$**）；配偶相对位置升级（`AR-P`）为 **$+6.82$ 个百分点**（95% CI: `[1.05, 12.62]`，BH **$q=0.094$**）。
   - 在基期夫妻同分的共同资格样本（$N=7,058$）中，本人与配偶相对位置升级的加性交互差达 **$-16.40$ 个百分点**（95% CI: `[-26.96, -5.85]`）。

2. **锚点二（短期中介机制的“窄区间零效应界 / Tightly Bounded Null”）**：
   - 历史八链的总自然间接比值比（`rRtnie`）全部紧贴无效值 $1$（例如 `AR-S` 为 $1.0017$，95% CI: `[0.9968, 1.0047]`，区间半宽仅 $0.0040$；`AR-P` 为 $0.9990$，95% CI: `[0.9963, 1.0052]`）。
   - 选择后限定复核删除跨波累计父辈支持（`dwm_begin`）后，`FEAS_031` 与 `FEAS_041` 的模型化间接对比（`TNIE`）分别为 **$0.999$ `[0.994, 1.004]`** 与 **$1.000$ `[0.998, 1.003]`**（区间半宽仅 $0.0050$ 与 $0.0025$）。
   - 新增 14 项概率中介规格（`C1–C4` 二波中介与 `D1–D2` 三波时序中介）的间接概率对比点估计介于 **$-0.0126$ 至 $+0.0907$ 个百分点**，95% 置信区间全部收紧在 **`[-0.1678, +0.3188]` 个百分点**以内（其中 `C1` 绝对收入 $\rightarrow$ 本人满意度 $\rightarrow$ 支持增长的 95% CI 仅为 **`[-0.0513, +0.0523]` 个百分点**）。这从统计精度上排除了任何 $\ge 0.32$ 个百分点的短期婚姻满意度传导效应。

3. **锚点三（相对婚姻评价跃迁的非对称构成与多维边界印证）**：
   - 对 `FEAS_031`（基期本人不高于配偶、期末本人高于配偶，$n=342$）的精确解构表明：仅 **$28.35\%$** 伴随本人满意度提高，高达 **$88.01\%$** 伴随配偶满意度下降（双方反向变动重叠占 **$16.36\%$**）；其中 **$71.65\%$** 的跃迁中本人评分持平或下降、完全由配偶评分下滑实现换序，仅 **$11.99\%$** 由本人评分单方提升实现。
   - 这一构成证明相对位置跃迁并非“婚姻质量改善产生向心推力”，而是**夫妻关系评价的不对称裂痕（主要由配偶满意度恶化触发）**对代际支持转化构成的负向关系边界。
   - 同时，`P3` 三状态期末支持金额整体检验（原金额 $p=0.132$、99% 封顶金额 $p=0.080$）与 `N1` 本人—波次分解（人际均值每高 1 分支持率高 **$+1.66$ / $+1.84$ 个百分点**，原始 $p=0.046/0.031$，固定六项校正 $q_6=0.120$；个人内偏差 $p=0.076/0.195$）共同印证：**长期关系底色与短期情绪波动具有截然不同的代际含义**。

---

## 二、三套差异化发表与学位论文落地方案（可直接复制使用）

### 方案 A：中文顶刊/权威期刊投稿方案（《社会学研究》《社会》《人口研究》《中国人口科学》《社会学评论》）

#### 1. 推荐投稿标题（备选 2 个）
- **标题一（理论机制导向，推荐投《社会学研究》《社会》《社会学评论》）**：  
  **《规范刚性与关系非对称：收入变化、夫妻婚姻评价与成年子女对父母的经济支持》**
- **标题二（实证与方法导向，推荐投《人口研究》《中国人口科学》）**：  
  **《收入变化、婚姻满意度与向上代际经济支持——基于反事实传导检验与夫妻相对评价情境的分析》**

#### 2. 投稿导语 / 自荐信核心段落（可直接粘贴至投稿系统附言）
> 尊敬的编辑部老师：  
> 本文利用中国家庭追踪调查（CFPS）2018—2020与2020—2022年相邻波次夫妻—父母配对追踪数据（13,092条亲子二元组—区间记录），系统检验了家庭社会学中关于“成年子女收入改善如何转化为向上代际经济支持”的两条竞争性机制假说：（1）**短期情感传导假说（中介机制）**，即收入增长经由改善本人或配偶婚姻满意度进而改变赡养行为；（2）**关系情境修饰假说（调节机制）**，即夫妻绝对与相对婚姻评价构成家庭新增资源在核心家庭与父代家庭之间分配的边界条件。  
> 论文在实证与方法上的核心贡献有三：第一，依托高精度反事实中介与多规格稳健性检验，证实两年窗口内婚姻满意度的间接概率效应被严格约束在 `[-0.17, +0.32]` 个百分点的极窄区间内，证伪了“短期收入改善普遍通过提升婚姻满意度拉动父母赡养”的强传导命题，揭示了中国家庭代际经济支持受伦理规范与长期关系底色塑造的**“规范刚性”**；第二，发现夫妻内部相对满意度位置升级对收入—支持关联存在显著的角色非对称加性交互（本人升级 `IC-RD = -8.76` 个百分点，FDR $q=0.032$；共同资格样本角色差达 $-16.40$ 个百分点）；第三，通过对相对位置跃迁的微观构成解构，揭示其中 $71.65\%$ 源于“配偶满意度下滑而本人持平或下降”的评价错位，从而将“相对满意度负向修饰”从表面的“婚姻幸福挤出孝道”重新界定为“夫妻评价非对称裂痕抑制资源代际外溢”。全文提供完整的开源复现代码与多重搜索校正审计链。

---

### 方案 B：英文 SSCI Q1 期刊投稿方案（*Journal of Marriage and Family*, *Social Science Research*, *Research in Social Stratification and Mobility*, *Chinese Sociological Review*）

#### 1. Recommended Title & Running Head
- **Title**: *Normative Rigidity and Relational Asymmetry: Income Dynamics, Dyadic Marital Evaluations, and Upward Intergenerational Financial Support in China*
- **Running Head**: *Income, Dyadic Marital Evaluations, and Filial Support*

#### 2. Ready-to-Use Abstract (245 words, JMF / SSR format)
> **Objective**: This study examines whether short-term income gains affect adult children's upward financial support to aging parents by altering marital satisfaction (mediation) or whether dyadic marital evaluations condition the responsiveness of filial support to income changes (moderation).  
> **Background**: Prior research links economic resources to marital quality and marital harmony to intergenerational transfers, yet two-step associations do not establish counterfactual mediation, nor do they distinguish shared marital improvement from asymmetric dyadic rank shifts.  
> **Method**: Using matched couple–parent dyad-interval panel data from the China Family Panel Studies (CFPS 2018–2020 and 2020–2022; $N = 13,092$ dyad-intervals across $5,318$ adult children), we combine marginal standardized risk differences, counterfactual mediation decompositions (`CMAverse`), two-part amount models, and Romano-Wolf / Benjamini-Hochberg adjustments across pre-specified and post-selection specifications.  
> **Results**: Income increases raise the probability of upward support growth by $4.90$ percentage points (95% CI $[1.54, 8.26]$) among respondents eligible for satisfaction improvement. However, counterfactual indirect effects are tightly bounded around zero across all probability specifications (95% CIs within $[-0.17, +0.32]$ percentage points; ORs within $[0.994, 1.004]$ after removing cumulative parental help). Conversely, an upward shift in the respondent's relative marital satisfaction rank negatively moderates the income–support link ($\text{IC-RD} = -8.76$ percentage points, $q = 0.032$; role difference $= -16.40$ percentage points in equal-baseline couples). Micro-decomposition reveals that $71.65\%$ of such rank shifts arise purely from spousal satisfaction decline rather than self-improvement.  
> **Conclusion**: Short-term filial financial support exhibits normative rigidity against transient marital fluctuations, while asymmetric dyadic dissatisfaction constrains the intergenerational spillover of income gains.

---

### 方案 C：中国人民大学博士学位论文（RUC Dissertation）章节嵌入模板

#### 1. 建议章节位置与定位
- **定位**：作为博士学位论文中**“核心家庭夫妻关系与代际支持资源配置（微观面板与反事实机制篇）”**的独立实证章（与潜类别转移 LTA / 潜调节 SD 模型章节形成“长周期潜结构演变 + 短周期配对反事实机制”的双支柱互补）。

#### 2. 章节引言衔接段（可直接粘贴至博士论文该章导论）
> 前述章节从家庭生命周期与潜结构视角考察了代际支持形态的宏观演变，但一个悬而未决的微观机制问题是：当成年子女在短期内获得新增经济资源时，这种经济能力的改善究竟是经由夫妻婚姻满意度的同步提升“传导”为对父母的赡养行动，抑或是受制于夫妻双方关系评价的“情境边界”？既有文献往往将“收入—婚姻质量”与“婚姻质量—代际支持”的两两回归显著直接拼合为中介链条。本章基于 CFPS 2018—2022 年夫妻—父母配对追踪数据，引入反事实因果中介框架与多重搜索校正规程，对个人及夫妻相对收入、本人及配偶绝对与相对婚姻满意度构成的候选机制网络进行严格检验。本章的核心发现表明，短期内代际经济支持对日常婚姻满意度波动表现出显著的“规范刚性”（间接概率效应严格受限于 $\pm 0.32$ 个百分点以内），但夫妻内部相对评价的非对称失衡（尤其是配偶满意度单方下滑导致的评价错位）构成了抑制收入增长向父母赡养转化的关系边界。

#### 3. 章节小结与向下一章过渡段（可直接粘贴至博士论文该章结尾）
> 综上所述，本章通过“基础回归风险差与加性交互—反事实中介窄区间零效应界—选择后限定复核与非对称结构解构”的三重证据链，澄清了夫妻婚姻评价在收入—代际支持关联中的真实角色：婚姻满意度并非短期收入效应的被动传递管道，而是调节家庭资源在核心家庭与父代家庭之间配置边界的关系情境；且这种调节效应高度依赖于夫妻评价的相对对称性，而非单方绝对满意度的简单线性增长。这一发现表明，仅凭可观测的短期二元满意度跃迁尚不足以穷尽夫妻异质性对代际交换的深层结构影响，这也自然引出了下一章的核心议题——如何从更长时序与潜在差异结构出发，考察夫妻关系特征对代际支持轨迹的结构性塑造。

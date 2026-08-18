# ch7 文献拡張収集（2026-08-18・Fable 調査）

第7章（経験構成型・TCE）のための候補リスト。全13件、書誌は一次資料（出版社・arXiv・AAAI OJS・Europe PMC・DBLP）で検証済み。既知文献との重複なし。**採否はオーナー判断待ち**。

## 系統1: TCE の計算モデル化・形式化（ch2 脚注 [^tce-computational] の裏付け）

1. Smith, R., Parr, T., & Friston, K. J. (2019). Simulating Emotions: An Active Inference Model of Emotional State Inference and Emotion Concept Learning. Frontiers in Psychology, 10, 2844. doi:10.3389/fpsyg.2019.02844
   - 感情概念の学習と情動状態の推論を能動的推論で形式化。ch2「計算モデルとしての先行研究がある」の裏付け本命
2. Joffily, M., & Coricelli, G. (2013). Emotional Valence and the Free-Energy Principle. PLoS Computational Biology, 9(6), e1003094. doi:10.1371/journal.pcbi.1003094
   - valence を自由エネルギーの負の時間微分として定式化した先駆
3. Taveter, K., & Kirikal, A. (2022). Prototyping an Architecture of Affective Robotic Systems Based on the Theory of Constructed Emotion. ICSR 2022 (Springer LNCS), pp. 558-575. doi:10.1007/978-3-031-24667-8_49
   - TCE をエージェントアーキテクチャに落とした数少ない実装研究。⚠ LNCS 巻番号のみ未確認（採用時に最終確認）

## 系統2: TCE への批判・論争の一次資料

4. Adolphs, R. (2017). How should neuroscience study emotions? by distinguishing emotion states, concepts, and experiences. Social Cognitive and Affective Neuroscience, 12(1), 24-31. doi:10.1093/scan/nsw153
   - **Barrett 2017 と同誌同号での正面からの対抗論文**。応酬の構図がそのまま使える（PMC でオープンアクセス）
5. Ekman, P. (2016). What Scientists Who Study Emotion Agree About. Perspectives on Psychological Science, 11(1), 31-34. doi:10.1177/1745691615596992
   - 基本感情説側の「大多数は普遍的感情に合意」調査論説。論争の相手側の到達点
6. van Heijst, K., Kret, M. E., & Ploeger, A. (2025). Basic Emotions or Constructed Emotions: Insights From Taking an Evolutionary Perspective. Perspectives on Psychological Science, 20(3), 377-391. doi:10.1177/17456916231205186
   - 対立を「別々の現象の説明」として解消する統合レビュー。論争の現在地。⚠ オンライン2023・誌面2025——引用年は採用時に統一

## 系統3: 2024〜2026 新着（LLM エージェント × 経験記憶）

7. Park, J. S., et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior. UIST '23. doi:10.1145/3586183.3606763 / arXiv:2304.03442
   - **書誌検証完了**: 実装が依拠する記憶スコアリング（relevance+recency+importance）の原典として引いて問題なし
8. Huang, L., et al. (2024). Emotional RAG: Enhancing Role-Playing Agents through Emotional Retrieval. IEEE ICKG 2024, pp. 120-127. doi:10.1109/ICKG63256.2024.00023 / arXiv:2410.23041
   - 気分依存記憶に基づく感情状態ベクトルでの記憶検索。affectus の類似検索の最近縁
9. Zhong, W., et al. (2024). MemoryBank: Enhancing Large Language Models with Long-Term Memory. AAAI 38(17), 19724-19731. doi:10.1609/aaai.v38i17.29946
   - 忘却曲線の指数減衰と想起強化を LLM 長期記憶に実装した代表研究。「この設計は記憶研究の定石」の支え
10. Zhang, Z., et al. (2024). A Survey on the Memory Mechanism of Large Language Model based Agents. arXiv:2404.13501
    - LLM エージェント記憶機構の包括サーベイ。位置づけの俯瞰用

## 系統4: 概念・カテゴリ化と感情語彙（culture_map の支持）

11. Barrett, L. F., Lindquist, K. A., & Gendron, M. (2007). Language as context for the perception of emotion. Trends in Cognitive Sciences, 11(8), 327-332. doi:10.1016/j.tics.2007.06.003
    - 言語文脈仮説の定礎論文。culture_map の理論的根拠
12. Gendron, M., Lindquist, K. A., Barsalou, L., & Barrett, L. F. (2012). Emotion words shape emotion percepts. Emotion, 12(2), 314-325. doi:10.1037/a0026007
    - 「語彙が構成を変える」直接の実験的証拠（PMC あり）
13. Jackson, J. C., et al. (2019). Emotion semantics show both cultural variation and universal structure. Science, 366(6472), 1517-1522. doi:10.1126/science.aaw8160
    - 2,474言語の分析で「感情語の意味構造は文化で変わるが valence・arousal の次元は普遍」。**本書の設計（2軸は共通基盤・語彙マップは差し替え）と同型の最重要候補**

## 調査エージェントの推奨

急所を固める3本: Jackson et al. 2019（culture_map と2軸普遍性の同時支持）・MemoryBank（忘却・想起強化の定石化）・Adolphs 2017（同誌同号の論争）。

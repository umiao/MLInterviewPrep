1. 迷宫问题 (Maze Solver) —— 高频核心题
4-5 个递进任务，难度由浅入深。

Q1：基础修复与格式控制（通常禁止使用 AI）
核心： 考察对原始 Codebase 的快速定位。
常见 Bug： 起始点/终点符号被路径符（如*）覆盖；打印格式不符合diff要求。
对策： 在打印逻辑中增加if-else逻辑，确保特殊标志位的显示优先级。

Q2：基础算法修复 (BFS/DFS)
常见 Bug： 缺少visited集合导致死循环。对策： 检查节点入队/入栈前的去重逻辑。
Q3：移动规则限制（指令门）
逻辑： 遇到>或<时强制改变移动方向。
对策： 修改get_neighbors或move方法，加入当前位置字符的条件判断。
Q4：钥匙与门 (Key & Door)
模型协同： 此处逻辑开始变复杂，可以开始调用 Claude 4.6 Opus 辅助。
算法调整： 必须重新定义visited状态。将(x, y)扩展为(x, y, collected_keys_bitmask)，因为拿到钥匙后需要“走回头路”。
Q5：特殊障碍物 (如炸弹 Bomb)
逻辑： 触发炸弹炸毁半径两格内的墙。
模型协同： 使用 Claude 生成处理爆炸半径坐标的get_affected_area辅助函数，并将其整合进搜索状态中。
总结和要点：BFS 复杂度的标准公式是 O(V + E)，套到迷宫问题上要分清两个维度：
•	状态空间 V：你的 visited 集合最多容纳多少不同的状态。Vanilla 是 W·H；带 k 把钥匙是 W·H·2^k；带 b 个一次性炸弹是 W·H·2^k·2^b。
•	每状态处理代价：出队后枚举多少邻居。4 邻接是 ×4，8 邻接是 ×8，马步是 ×8。这是常数因子，可以吸收进大 O，但显式写出来便于变种适配。
关键洞察：加了 visited 之后，路径长度从复杂度里消失。(4+k)^n 之类的式子来自"无去重 DFS 的路径树展开"，加了状态去重就降级成线性。真正的指数爆炸来源是状态维度的增加（多一种机制 → 多一个 mask），不是邻接数。
实战量级感：
•	k ≤ 8：2^k ≤ 256，bitmask BFS 随便跑。
•	k ≈ 15-20：开始紧张，要看网格大小。
•	k ≥ 25：放弃 bitmask，换启发式搜索或 TSP-like 建模。
________________________________________
钥匙状态：bitmask 编解码
钥匙单调不减（拿到不会丢），所以 mask 在搜索过程中只增不减，但 BFS 仍按完整状态 (x, y, mask) 去重。
python
# 拿到钥匙 c (假设 c 是 'a'-'z')
new_mask = mask | (1 << (ord(c) - ord('a')))

# 检查是否持有钥匙 c（用于开门）
has_key = mask & (1 << (ord(c) - ord('a')))

# visited 用完整状态做 key
visited = set()
visited.add((x, y, mask))
这几行要练到肌肉记忆，面试现场不要让 AI 帮写——浪费时间且容易抄错位运算。
________________________________________
炸弹：bombMask 的查表预处理
朴素想法的问题：把"被炸毁的格子集合"直接塞进状态会让 visited 爆炸（5 个格子 × 每格 2 状态 = 32 倍状态空间，且不通用）。
正确做法：状态里只存 bomb_mask（哪些炸弹引爆了），墙是否消失通过查表函数从 mask 反推。本质是把"确定性派生信息"从状态里剥离出去。
python
# 预处理：每个炸弹 -> 它能炸毁的墙坐标集合
affected_walls = {}  # bomb_id -> set of (x, y)
for bid, (bx, by) in enumerate(bomb_positions):
    affected_walls[bid] = compute_blast_area(bx, by, radius=2)

# 查询：在当前 bomb_mask 下，(x, y) 是否仍是墙
def is_wall(x, y, bomb_mask):
    if grid[x][y] != '#':
        return False
    for bid in range(num_bombs):
        if bomb_mask & (1 << bid):
            if (x, y) in affected_walls[bid]:
                return False  # 已被炸毁
    return True
收益：状态空间从"5 格 × 32 种局部组合"降到"b 个炸弹 × 2^b"，且可扩展到任意爆炸半径——半径 5 还是 50，状态空间不变。
触发逻辑：踩到炸弹格子时 new_bomb_mask = bomb_mask | (1 << bid)。注意炸弹通常一次性，和钥匙一样是单调不减的 mask。
________________________________________
引导砖（> < ^ v）
题意确认：不是强制传送，而是约束下一步的可选方向。所以只需修改 get_neighbors：
python
def get_neighbors(x, y, mask, bomb_mask):
    c = grid[x][y]
    if c == '>': dirs = [(0, 1)]
    elif c == '<': dirs = [(0, -1)]
    elif c == '^': dirs = [(-1, 0)]
    elif c == 'v': dirs = [(1, 0)]
    else: dirs = [(0,1), (0,-1), (1,0), (-1,0)]
    # ... 然后正常生成 neighbors
不需要担心传送链或环，因为引导砖只是裁剪选项集合，BFS 框架不变，复杂度也不变。
________________________________________
路径打印（Q1 的优先级陷阱）
显示优先级（从高到低）：起点 S / 终点 E > 路径 * > 钥匙/门/炸弹 > 普通空地。打印时按优先级逐层覆盖：
python
def render(grid, path):
    out = [row[:] for row in grid]  # 深拷贝
    for (x, y) in path:
        if out[x][y] not in ('S', 'E'):  # 保护起终点
            out[x][y] = '*'
    return '\n'.join(''.join(row) for row in out)
Diff 翻车点：行尾空格、末尾换行符、Windows/Unix 换行差异。提交前用 diff -u expected actual 肉眼对一遍。
________________________________________
完整状态去重：最常见的 bug
加了机制后 visited 必须用完整状态做 key，不能再用 (x, y)：
python
# 错误（会漏掉"绕路捡钥匙再回来"的情况）
visited.add((x, y))

# 正确
visited.add((x, y, mask, bomb_mask))
这是带状态扩展的 BFS 最容易翻车的地方。每次写完代码先 grep 一下 visited，确认 key 是完整状态。
________________________________________
AI 协同的边界
适合让 AI 做	自己做更快/更靠谱
生成爆炸半径、坐标变换 helper	bitmask 编解码（idiom 化）
把已设计好的状态机翻译成代码	状态空间设计（核心考点）
生成边界 case 测试输入	visited 的 debug
解释陌生代码	复杂度分析（AI 经常给错式子，让它 review 而非主导）
底线：AI 给的复杂度公式一定要自己复算一遍。状态空间设计能解释清楚比代码跑得过更重要——面试官会追问"为什么要这样建模"。
________________________________________
速查清单（面试前 5 分钟过一遍）
•	 状态空间维度想清楚了吗？每个新机制都要问"要不要加 mask 维度"。
•	 visited 用的是完整状态，不是 (x, y)。
•	 bitmask 操作 |=、& 写对了，没有把 1 << 的位置算错。
•	 派生信息（炸弹炸过的墙）通过查表算，不进 visited。
•	 起点/终点的打印优先级保护了。
•	 复杂度能口头分析：状态数 × 邻接数，分别说出每一项的含义。
•	 k 或 b 太大时，能说出 bitmask 不再可行的临界点和替代思路















2. 最大唯一字符子集 (Max Unique Character Subset)
给定单词列表，找出单词子集，要求子集内单词无重复字母，且覆盖的唯一字母总数最多。
初级 (Q1-Q2)： 针对小规模数据（如 12 个单词），使用回溯法 (Backtracking)。
高级 (Q3-Q4)： 面对万级大数据集。
AI 协同策略： 像 Claude 4.6 Opus 这样的模型在处理这种纯算法优化时非常强大。
引导模型进行：预处理： 将单词转化为 26 位 Bitmap，并剔除本身含有重复字母的无效单词。
剪枝： 已达到 26 个字母时立即返回。算法升级： 若递归过慢，引导 Claude 使用 状态压缩 DP (State Compression DP)，记录(bitmap, subset)以减少重复计算。
第三四问可以dp存<bitmask(number+letter用Long), Node>，bitmask number+letter用Long，并且做一下单词自身字母和数字的去重，Node里有previous指针指向前一个node这样内存不会炸，类似二维数组找路径类的输出路径作为结果的题目存previous指针的思路，并且在达到长度36的时候直接剪枝输出，三四问都可以跑过; AI coding，找最大的包含unique character的subset，基础解法先来个backtracking，第二个test case优化一下路径，比如已经找到26个字符了就return，第三个test case用DB+state tracking，需要记录上一个state的bitmap+subset，这样找到以后就能reconstruct路径，最好再预处理一下testcase，比如abc，cba这种anagram算重复的，可以加个visited去重，这轮重点不是使用AI而是展示你对AI写的code的理解和思考

给 AI 的 Prompt
把下面这段直接喂给模型，配合"已知最朴素 backtracking 写法跑不过大数据集"的背景就能引导出正确实现：
我有一个"最大唯一字符子集"问题：给定单词列表，选出一个子集使得子集内所有单词的字母两两不重叠，且覆盖的不同字母总数最多。返回这个单词子集本身（不是字母数）。
数据规模可达万级单词，请用状态压缩 DP 实现，并满足以下约束：
1.	预处理： (a) 把每个单词转成 26 位 bitmap；(b) 丢弃自身包含重复字母的单词（即 popcount(mask) != len(word)）；(c) 对相同 bitmap 的单词（包括 anagram）只保留一个代表。
2.	DP 设计： 用 dp: dict[int, int] 存"已达到的 mask → 把我们带到这个 mask 的单词 index"。不要用带 prev 指针的 Node 类；利用一个数学性质来省内存——因为 DP 转移要求 prevMask & wordMask == 0，所以 newMask = prevMask | wordMask = prevMask ^ wordMask，两边再异或 wordMask 即可反推 prevMask。
3.	转移： 对每个单词外层循环，内层遍历当前 dp 的snapshot（避免同一单词被重复使用——这是 0/1 背包性质）。同一个 mask 不要重复写入。
4.	剪枝： 一旦 mask 覆盖全部 26 位（或题目约定的 36 位包含数字时取 (1<<36)-1）立即停止并返回。
5.	路径重建函数： 从 best_mask 出发，循环执行 w = dp[cur]; path.append(words[w]); cur ^= masks[w]，直到 cur == 0。
请用 Python 实现，关键步骤加注释解释为什么这样写（特别是 XOR 反推那一步和 snapshot 那一步），最后给一个小测试用例验证既能输出最大字母数也能正确重建出单词列表。
一个值得记住的元规律
这个 XOR trick 能用，根本原因是 DP 转移的约束（不相交）让 OR 退化成了 XOR。换到别的题目，比如"允许字符重叠取最多覆盖"，就不能这么省了——因为 prevMask | wordMask 时存在多个不同的 prevMask 都能产生同一个 newMask，反推不再唯一。
所以面试时如果你想秀一手，可以这样表述："这道题的不相交约束让我可以把 prev 指针折叠进 XOR 关系，dp value 就是一个整数。"——这会让面试官立刻知道你不仅会写 DP，还看清了这个 DP 特有的代数结构。这种"我看到了别人没看到的不变量"的瞬间，比任何复杂代码都更能体现思考深度。





---
3. 好友推荐系统 (Friend Recommendation)
Q1：逻辑漏洞修复： 修复valid_recommend。通常 Bug 在于未排除“用户本人”或“已是好友的人”。
Q2：利用 AI 实现： 实现random_recommend。重点在于提供清晰的类结构 Prompt 给 AI，让其快速生成符合接口的代码。
Q3：算法设计与评估： 讨论推荐指标（如 Mutual Friends）。
模型协同： 询问 Claude：“基于现有的User类属性，如何实现一个 Top-K 共同好友推荐算法？”并让其分析时间复杂度。

第一小问是fix一个什么valid_recommend function to pass the test case，面试官说这一问不能用AI很容易能fix，所以浏览了一下test case和那个什么valid_recommend function，可能还看了点别的，就发现了那个什么valid_recommend的input是一个user和一个list of user，没有判断list of user有没有包含自己，所以两行代码fix了
第二小问面试官说从这里开始可以用ai了，是去implement一个什么random_recommend function，一开始用AI然后直接paste进去不works，后来迭代了几轮后就可以了，直接贴进去，跑，it works
第三问面试官贴了一点题出来，我没来得及看，他说如何衡量一个好友推荐算法好不好，我用ai generate了几条，然后我用ai generate了一些ideas，然后面试官问ai回答里哪些能用，我去看User class有哪些attributes，它只有一个id一个currentFriends，没有各种别的什么性别生日group啥的，所以回答只有mutual friends和另一个啥，忘了，能用。然后面试官叫我用一个新的file实现mutual friends，我用ai generate code，面试官说同时generate test file，然后我照做了，然后贴进去跑。

L1 第一层：无 AI 的 Bug Fix（对应 Q1）
考点 1.1 — 好友推荐函数的"必查清单"
看到 valid_recommend(user, candidates) 这种签名，自动按以下顺序检查：
排除自指（user 不在 candidates 结果里）、排除已有好友、去重、对称性（A→B 和 B→A 的处理）、空集边界、类型边界（User 对象 vs user_id 比较方式）。考点 1.2 — 从 test 名反推 bug。 测试名通常直接暴露考点：test_excludes_self 就是在告诉你"自指没排除"。先扫测试名，再看 assertion，再回函数找缺失分支。
考点 1.3 — 修复时不要顺手重构
只修必要的两行，别动其他逻辑。考官在测的是"精准定位"，不是"代码品味"。多动一行就多一个 bug 的可能性。
________________________________________
L2 第二层：AI 辅助实现的迭代心法（对应 Q2）
考点 2.1 — 第一发 Prompt 的完整结构
第一次 paste 不 work 几乎都是 prompt 给得不够。第一发必须包含：完整类定义、相关函数签名（让 AI 知道接口约定）、一两个测试用例（让 AI 知道期望行为）、明确的约束（依赖、返回类型、长度规则）。
评分标准：第一发 prompt 给得够厚，AI 一次过的概率从 30% → 80%。
考点 2.2 — Paste 前的快速扫描
AI 输出别直接 paste。三件事扫一遍：属性名是否匹配（user.friends vs user.currentFriends）、方法签名是否吻合、边界条件是否齐全。这一步比 paste 后 debug 快十倍。
考点 2.3 — 增量式 Debug
第二发 prompt 不要重新描述需求，直接贴：这是你给的代码 + 这是错误 traceback + 请修复。这样 AI 改的是 delta，不是从头来过。
考点 2.4 — 迭代失败的止损信号
迭代两轮还不过，停下来。说明需求描述本身有歧义，或者你漏看了某个类属性 / 隐含约束。继续盲迭代只会越改越乱。
考点 2.5 — 常见 AI 幻觉模式
提前知道 AI 在这类题里会幻觉什么：编造不存在的属性（如假设 User 有 interests）、用错 hash（在没实现 __hash__ 的对象上用 set）、引入多余依赖（如硬塞 numpy）、忽略给定的辅助函数（自己重写 valid_recommend）。
________________________________________
L3 第三层：AI 输出的判断与过滤（对应 Q3 前半部分）
考点 3.1 — "AI 给十个，可用两个"的过滤逻辑
AI 看到"好友推荐"会列出十几种方案，但能用的取决于 User 类有什么数据。过滤步骤：列出 AI 所有建议、对每条标注"需要什么数据"、对照 User 类属性删掉做不到的、剩下的按实现复杂度排序。
考点 3.2 — 好友推荐指标的"光谱"知识
按数据要求从低到高排：
只需要图结构的：mutual friends count、Jaccard 相似度、Adamic-Adar 指数、Resource Allocation 指数、2-hop 路径数。
需要 demographic / profile 的：年龄/地区匹配、共同 group、相同学校 / 公司。
需要行为日志的：共同访问页面、消息频率、登录时段重合。
面试用法：被问"还能怎么改进"时，从同一光谱往右挪一格（mutual friends → Adamic-Adar）显得有领域常识；跨光谱挪（mutual friends → 兴趣推荐）通常会被反问"数据从哪来"。
考点 3.3 — Adamic-Adar 的一句话原理
如果只能记一个超出 mutual friends 的指标，记 Adamic-Adar：共同好友按其度的反对数加权。直觉是"你和我都认识一个只有 5 个朋友的人，比都认识一个有 5000 朋友的网红，更能说明咱俩关系近"。一句话能讲清就是会用。
________________________________________
L4 第四层：算法实现 + 复杂度分析（对应 Q3 后半部分）
考点 4.1 — Top-K Mutual Friends 朴素实现
遍历所有候选 → 对每个做 set 交集 → heap 取 top k。
复杂度：O(n · f + n log k)，n 总人数，f 平均好友数。
考点 4.2 — 2-Hop 优化
从 target 的好友出发，遍历好友的好友，用 Counter 累加。复杂度 O(f²)。
何时用：n 大 f 小的真实社交网络（n 上亿、f 几百）。
前提：要有 user_id → User 的查找字典；如果输入只是 list of User，朴素版更合适。
考点 4.3 — "基于输入接口选算法"的思考表述
考官追问"为什么不一开始就用 2-hop"时，标准回答模式：先讲约束，再讲算法。例："2-hop 需要 O(1) 查表，所以前提是有 user_lookup dict。如果输入只是 list 我就用朴素版；如果允许预处理建索引就用 2-hop。"
这种回答展示的是工程取舍，不是算法熟练度。
考点 4.4 — 复杂度分析的"两段论"
讲复杂度分两步：先讲主导项（O(n·f) 是主导，O(n log k) 是次要的），再讲优化方向（哪一步浪费了，怎么省）。只讲数字不讲洞察的复杂度分析是低分回答。
________________________________________
L5 第五层：测试生成的覆盖意识（Q3 隐藏考点）
考点 5.1 — Mutual Friends 测试的最小覆盖集
正常排序、自己排除、已有好友排除、零共同好友、并列处理（稳定 vs 任意）、K > 候选数、空 friend list。
考点 5.2 — 让 AI 生成测试的 Prompt 模式
不要说"写测试"，要说"写测试覆盖以下场景：[列出 5-7 条]"。前者得到笼统的 happy path 三件套，后者得到能用的测试套件。
考点 5.3 — 测试也要 paste 前扫一眼
AI 生成的 test 也会幻觉——比如调用一个不存在的 helper、assert 一个错误的预期、import 多余的库。Test 文件也要按 L2 的扫描原则过一遍。
________________________________________
L6 顶层：面试中的"元能力"展示
这一层不是技术点，是怎么让考官看见你的判断力。同样的代码，不同表述差一个等级。
考点 6.1 — 主动声明"我不采纳什么"
讲"为什么不用 AI 的某个建议"比"我用了什么"更值钱。例："AI 建议基于 interest 做推荐，但 User 类没有 interest 字段，所以排除。"——这一句话直接展示了 L3 的判断力。
考点 6.2 — "够用即可"的工程取舍
面试时间有限。明确说出"我先实现 mutual friends，因为最简单且时间够；Adamic-Adar 是可选的优化方向"。考官想看的是有取舍意识的工程师，不是炫技的人。
考点 6.3 — 把 AI 当"协作者"而不是"代写"的措辞
外化思考过程：边操作边讲"我现在让 AI 生成 X，因为 Y；它给了 Z，但我要改 W，因为类里没有 V"。这种自言自语式的解说，让考官看见你的判断节奏。沉默地 paste-试-paste-试是最低分的姿态。





---
4. 其他 AI Coding 题目 (MLE/实习向)
稀疏矩阵 (Sparse Matrix) 运算：
重点： 实现稀疏向量点积或矩阵乘法。
AI 引导： 让 AI 对比 COO、CSR 等不同存储格式在乘法运算中的性能差异。
线性回归手推实现：
逻辑： 给定点集，最小化 MSE，推导并实现 $\hat{y} = wx$。
AI 协同： 如果忘记公式，可以让 Claude 4.6 Opus 快速推导其导数并给出闭式解（Closed-form solution）的代码实现。

稀疏矩阵 & 线性回归 复习资料
一、稀疏矩阵运算
核心思路（一段话总览）
稀疏向量/矩阵运算的核心是让 NNZ（非零元个数）取代维度成为复杂度主导项。做点积或乘法时，先比较两边稀疏度，找更稀疏的一方作为入口和瓶颈，把它转成坐标形式（COO 三元组：row、col、val），然后永远遍历稀疏的那一方，对稠密的一方用哈希/二分定位即可。常见三种存储格式：COO（三元组、构建快）、CSR（按行压缩，row_ptr + col_idx + val，SpMV 友好）、CSC（按列压缩，SpMV^T 和取列友好）。工业界惯例是构建期用 COO，运算期 .tocsr() / .tocsc()——SciPy 就是这么设计的。CSR × CSC 是经典乘法搭配：A 取行、B 取列，归约成稀疏向量点积。
稀疏向量点积（双指针）
def sparse_dot(v1, v2):
    """v1, v2: List[(idx, val)]，按 idx 升序"""
    i, j, res = 0, 0, 0.0
    while i < len(v1) and j < len(v2):
        if v1[i][0] == v2[j][0]:
            res += v1[i][1] * v2[j][1]; i += 1; j += 1
        elif v1[i][0] < v2[j][0]:
            i += 1
        else:
            j += 1
    return res
复杂度 O(nnz1 + nnz2)。若一稀一稠，遍历稀疏端 + 哈希查稠密端 → O(nnz_small)。
矩阵乘法 < O(n³) 的主流算法
算法	复杂度	原理
Strassen (1969)	O(n^2.807)	分治：把 2×2 分块乘法的 8 次子乘法 重组为 7 次子乘法 + 18 次加法，递归下去就突破立方界。
Coppersmith–Winograd 系列	~O(n^2.37)	借助张量秩 (tensor rank) 上界构造的递归方案，常数极大，只有理论意义。
当前最优 (Alman–VW, 2024)	~O(n^2.371)	同系列改进。
工业界实际做法：BLAS 的 GEMM 仍是 O(n³) 朴素三重循环，但靠 cache blocking、SIMD/AVX、多线程把常数压到极致——比 Strassen 快、数值更稳定。理论复杂度 ≠ 实际性能。
________________________________________
二、线性回归 (Linear Regression)
推导结论
最小化 $L(w) = |Xw - y|^2$，求导得 $\nabla_w L = 2X^T(Xw - y)$。关键点：求导出来是 $X^T$ 而不是 $X$，是为了维度对齐（$\nabla_w L$ 必须是 $d \times 1$，$Xw - y$ 是 $n \times 1$，所以前面乘 $X^T \in \mathbb{R}^{d \times n}$）。令梯度为 0：
$$\boxed{w = (X^T X)^{-1} X^T y}$$
三种实现
np.linalg.inv(X.T @ X) @ X.T @ y    # 教科书；显式求逆，慢且不稳
np.linalg.solve(X.T @ X, X.T @ y)   # 推荐；LU 分解解方程，避免显式求逆
np.linalg.pinv(X) @ y               # 最稳；SVD 伪逆，能处理 X^TX 奇异
复杂度均为 O(nd² + d³)。d 很大时改用 GD/SGD。
________________________________________
三、高频 Follow-up（原地作答）
Q: 加 L2 正则（Ridge）闭式解？ 本质是在 $X^TX$ 上加 $\lambda I$，解为 $w = (X^TX + \lambda I)^{-1}X^Ty$。顺带变得永远可逆（$\lambda I$ 把所有特征值抬高了 $\lambda$）。
Q: 为什么 Lasso (L1) 没有闭式解？ $|w|$ 在 0 处不可导（有跳变点 / 次梯度），整体不能一次性解出。但逐元素 (elementwise) 固定其他维度时，单个 $w_j$ 的子问题可解析求解，得到 soft-thresholding 算子 $\text{sign}(z)\max(|z|-\lambda, 0)$——这是 coordinate descent / ISTA 的基础。
Q: 特征共线 (collinearity) 怎么办？ 共线意味着 $X^TX$ 离奇异更近一步（条件数爆炸），$\inv$ 数值不稳。处理：(a) 加 L2 → Ridge；(b) 用 pinv 走 SVD；(c) 删冗余特征 / PCA 降维。
Q: Batch GD vs Mini-batch vs SGD？
•	Batch：梯度无偏且方差小，但每步贵、易陷局部极小/鞍点。
•	SGD：单样本，方差大，噪声反而带来探索性，能跳出鞍点。
•	Mini-batch：折中，兼顾无偏性近似 + 探索性 + 硬件并行（GPU 友好），是事实标准。
Q: 稀疏向量没排序怎么办？ 丢一边进哈希表 {idx: val}，遍历另一边查表，期望 O(nnz1 + nnz2)。
Q: 稀疏矩阵转置？ CSR ↔ CSC 互为转置——不需要真做转置，换个视角读就行，O(1)。


5. Compiler Optimization
Problem Statement
给了几个folder，有test.py，test file文件和src文件。目标是优化complier 的time和mem。
example：
instruction1.txt
res1 = var1 + var2
res2 = var3 - var4
res3 = res2 + var5
res = res1 + res3

instruction2.txt
res1 = var1 * var2
res2 = var3 - var4
res3 = res2 / var5
res = res1 + res3

instruction3.txt
res1 = 10 * var2
res2 = var3 * 100 - var4
res3 = res1 / 2
res = res2 + res3

def extract_time_and_mem_cost(instruction):
                TODO
                return time, memunit test：

assert (extract_time_and_mem_cost('test/instruction1.txt'), 14)里面的具体数字这里有坑，我稍后说。GPT根据test1和test2的条件实现了代码，就是简单的operator check：
('+', '-', '='）cost=1
('*', '/') cost = 5于是我顺利的把test1和test3搞定了。

但是后面test4 到 test7一直报错。直到最后5分钟interviewer才提示我看看extract_time_and_mem_cost在干嘛。他提示说那些cost number可能是错的，我就GPT，1和5是哪里来的，然后GPT说它自己推理的。然后我问interviewer 我不懂compiler，但是有univeral的定义吗？他说没有。然后我一直让GPT 重新infer，最后时间不够了。

核心思路（一句话）
把 test cases 当作 spec 的一部分而不是验证手段，把未知的 cost 参数当成回归问题，把代码优化和参数拟合当成两个可分离的子问题，先固定一个推另一个。
三阶段骨架
阶段 A：建模（不写代码，只列结构）
把问题形式化成：
cost_total = f(features(optimize(parse(input))))
              ─────  ────────  ──────  ──────
              拟合     可选       已知     已知
四个组件里哪些已知、哪些未知，决定了你下一步干嘛。这道题里 parse 已知，optimize 可选/未知形式，features 候选有限，f 是参数未知的线性函数。
阶段 B：参数拟合（先假定 optimize = identity）
不优化、直接数 op，用 lstsq 反推 cost。如果拟合上了 → cost model 不要求优化，直接收工。如果拟合不上 → 进入阶段 C。
阶段 C：优化形式搜索
枚举几种主流优化组合（CSE / constant folding / DCE / inline），每种组合下重做阶段 B，看哪一种让所有 test 残差为 0。
关键洞察：阶段 B 和 C 可以独立验证，不要一开始就把它俩耦合起来想，会爆炸。
Meta-Prompt 模板
下面这个模板可以直接喂给 GPT/Claude，针对这类"给 example 反推规则"的题。占位符用 {{...}} 标出：
我有一道"从 test cases 反推未知规则"的题。请按以下结构帮我分析，
不要凭直觉给常数，所有数值必须从 test 中推导。

═══ 1. INPUT ═══
- Function signature: {{def f(...) -> ...}}
- All test cases (input + expected output):
  {{完整列出，包括输入文件内容}}
- Constraints from problem statement: {{有哪些已知规则}}

═══ 2. UNKNOWNS ═══
列出所有未知量，分类为:
  (a) 数值参数 (适合用回归求解)
  (b) 离散结构选择 (适合枚举或搜索)
  (c) 函数形式 (线性? 取 max? 分段?)

═══ 3. FEATURE EXTRACTION ═══
为每个 input 提取候选特征向量。先列尽量全的特征，
标注哪些是"必然相关"哪些是"可能相关":
  - {{特征 1}}: 必然 / 可能 / 备选
  - ...

═══ 4. EQUATIONS ═══
把每个 test 写成一个方程:
  test_k: Σ c_i · f_i^(k) = output_k
列出方程数 vs 未知数，判断 over/under/exactly determined。

═══ 5. SOLVE ═══
- 用 numpy.linalg.lstsq 解
- 报告残差: 全 0 / 系统性偏差 / 随机
- 如果残差非 0，提出最可能漏掉的特征是什么并说明理由

═══ 6. VALIDATE ═══
用解出的参数回代验证每个 test，给出每个 test 的
  predicted vs expected 对比表

═══ 7. ITERATE ═══
如果验证失败，按以下顺序假设并重试:
  Step 1: 加入优化 pass (CSE / folding / DCE / inline)
  Step 2: 改变函数形式 (线性 → 分段线性 / max / peak)
  Step 3: 加入结构性特征 (peak liveness / critical path)
每次改动只改一个变量，记录哪些假设有效。

═══ OUTPUT ═══
最终给我:
  - 拟合出的参数表
  - 必要的优化 pass 列表
  - 残差为 0 的证明（所有 test predict == expected）
  - 实现 f(...) 的最简代码
配套的代码骨架
下面这个骨架对应阶段 B 和 C，把"猜 cost"和"做优化"解耦：
python
import numpy as np

# ── 1. Parse: 字符串 → IR ────────────────────────────
def parse(text):
    """ 'res1 = var1 + var2' → ('res1', '+', 'var1', 'var2') 之类 """
    ...

# ── 2. Optimize: IR → IR (可选 pass 组合) ──────────────
def optimize(ir, passes=()):
    for p in passes:
        ir = p(ir)
    return ir

# 各个 pass 单独写、单独可测
def constant_fold(ir): ...
def dead_code_elim(ir): ...
def common_subexpr(ir): ...
def inline_all(ir): ...

# ── 3. Featurize: IR → 特征向量 ───────────────────────
FEATURE_NAMES = ['n_add', 'n_sub', 'n_mul', 'n_div',
                 'n_assign', 'n_unique_vars', 'peak_live']
def featurize(ir):
    return np.array([...])  # 长度 = len(FEATURE_NAMES)

# ── 4. Fit: 用所有 test 反推 cost ─────────────────────
def fit(test_cases, passes=()):
    """ test_cases: [(ir, expected_time), ...] """
    X = np.stack([featurize(optimize(ir, passes)) for ir,_ in test_cases])
    y = np.array([t for _,t in test_cases])
    coef, residuals, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    return coef, pred, y, np.abs(pred - y).max()

# ── 5. Search: 枚举 pass 组合找 max_error == 0 的 ────
from itertools import combinations
ALL_PASSES = [constant_fold, dead_code_elim, common_subexpr, inline_all]

for k in range(len(ALL_PASSES)+1):
    for combo in combinations(ALL_PASSES, k):
        coef, pred, y, err = fit(test_cases, passes=combo)
        if err < 1e-9:
            print(f"FOUND: passes={[p.__name__ for p in combo]}")
            print(f"       coef={dict(zip(FEATURE_NAMES, coef))}")
            break
这套结构的好处：每一层都可以独立调试，残差非 0 时你能精确定位是 特征不够 还是 优化 pass 不对。
给人类用的"心法版" meta-prompt
如果不喂 LLM，自己面试时脑子里跑的 checklist 更短：
1.	"这题里有没有看起来是常数、其实是未知数的东西？" — 就是这道题面试官那句"没有 universal 定义"想点醒你的。
2.	"test 给的数字是验证我，还是定义问题？" — 如果是后者，方程组思路立刻启动。
3.	"我能不能把 '推规则' 和 '应用规则' 分两步做？" — 别耦合。
4.	"先用最朴素的模型拟合一次，看残差告诉我什么" — 不要 upfront 就上复杂模型。
5.	"残差是系统性还是随机？" — 系统性 = 漏特征，随机 = 模型形式错。
一个值得记住的失败模式
你这次踩的坑可以总结成一句话："LLM 给的常数永远要问'你怎么得到这个数的'。" 如果它答"标准做法"或"惯例"，且这个领域 实际上没有标准，那这个数 100% 是幻觉。这道题里 1 和 5 就是典型——LLM 知道乘法比加法贵（这部分对），但具体倍数是它编的（这部分错）。
下次的反射动作应该是：任何 LLM 给出的没有引用源的具体数值，先假设是错的，除非能从问题约束里独立验证。






6. AI Coding新题 给一个list of words,找出word包含其他word的单词
[category, cat] = category,solver已经实现过了
(1) 分析已经实现代码的时间复杂度，空间复杂度,不能用ai
(2)给出优化方案，和预计的时间和空间复杂度（不用ai），然后实现，这时候可以用ai


D
Copy
AI 辅助算法面试 · 完整复习资料
主线案例：在一组 word 中找出"包含其他 word 作为子串"的单词 适用场景：Anthropic 风格的"分阶段、可控使用 AI"的 coding 面试
________________________________________
第 0 部分：核心理念
AI 时代的 coding 面试不再考"能不能写出代码"，而是考"能不能精确指挥 AI 写出正确、高效、健壮的代码"。考察重点已经从实现能力转向系统思考能力——你必须先在脑中建立完整的算法设计，再让 AI 当你的"打字员 + 语法纠错员"。
面试官想观察的核心信号：
1.	你能否独立分析复杂度（不依赖 AI）
2.	你能否估算理论最优下界（这决定了优化的天花板）
3.	你能否列出多层级解法并清晰对比取舍
4.	你能否精确表达算法意图给 AI
5.	你能否 review AI 的输出找到逻辑或复杂度问题
落到行为上，分阶段题目（一阶段不能用 AI，二阶段可以）就是在筛选能不能区分这两种能力的人。
________________________________________
第 1 部分：与 AI 协作的 6 步框架
Step 1：澄清问题边界（Clarify）
不要假设。本题的潜在歧义至少有：
•	"包含"是子串包含、前缀包含、还是后缀包含？示例 [category, cat] 区分不出来
•	是否区分大小写？unicode 还是 ASCII？
•	词可以重复吗？重复词算"包含自己"吗？
•	词长度上限？list 大小？是否流式？
•	输出是 word 本身，还是 (word, contained_word) pair？要去重吗？
Prompt 模板：在动手前先问 AI 或面试官——"请列出这道题在题面上不明确、需要澄清的点。"
这一步不仅是技术上的需要，也是面试中的信号——主动澄清显示工程成熟度。
Step 2：估算理论下界（Lower Bound）
这是最关键也是最容易被跳过的一步。下界回答的问题是："我做到多快算到顶了？"知道下界，才能判断当前方案是否还有优化空间，避免过度优化或优化不足。
下界的常见来源：
•	输入下界：必须读完所有输入。本题至少 Ω(N·L)
•	输出下界：必须产出全部结果。本题：Ω(|输出|)
•	信息论下界：比较模型下排序需要 Ω(n log n)
•	不可避免工作：每个潜在答案至少要被验证或排除一次
本题的下界：Ω(N·L)。任何 N²·L 或更慢的方案都还有优化空间。这告诉我们 brute force 不够，trie 路线值得追求，但比 N·L 更激进的优化（除非命中数本身很小）通常达不到。
Step 3：列出解法谱系（Solution Ladder）
从朴素到精妙，列 3-5 层。每层给复杂度。这是给面试官看你思维广度的最好方式，也帮你做出有依据的取舍。具体见第 2 部分。
Step 4：选型（Pick the Sweet Spot）
不一定选最优。要平衡：
•	实现复杂度 vs 性能提升
•	出错风险 vs 时间预算
•	面试官想看的深度（基础题 vs 难题信号不同）
话术示例：
"我可以给您实现 trie 子串版，O(N·L²)，30 行代码确定能跑过；或者升级到 Aho-Corasick，O(N·L)，但代码 80+ 行。考虑到面试时间，我建议先实现前者验证逻辑正确，如果时间还充足再升级。可以吗？"
主动提出 trade-off 比沉默地选一个方案更专业。
Step 5：AI 协作的分工原则
你做	AI 做
选算法、设计方案	写样板代码
推导复杂度	处理语法细节
列边界条件	生成测试用例
Review 代码逻辑	解释陌生 API
验证最终复杂度	重构、改名
最重要的反模式：让 AI "想个方法"或"给最优解"。这等于把考察的核心能力让出去。AI 给的解法你看不懂或不会复杂度分析时，整套答辩都会塌。
Step 6：验证（Verify）
•	跑 edge case：空 list、单词、重复词、空串、单字符词、超长词
•	真读 AI 的代码（不是扫一眼），关注循环边界、index、early exit
•	拿一个具体输入，沿着代码手算一遍，看输出是否符合预期
•	Validate 最终复杂度符合你的预期，而不是 AI 写出来"看起来很对"
________________________________________
第 2 部分：本题的解法谱系
Level 0：Brute Force - 最坏 O(N²·L²)
python
def find_containing(words):
    result = []
    for w in words:
        for o in words:
            if w != o and o in w:
                result.append(w)
                break
    return result
要点：
•	双重循环 N²
•	o in w 在 CPython 内部是 Crochemore-Perrin 的变体，最坏 O(|w|·|o|)，平均接近 O(|w| + |o|)
•	因此最坏 O(N²·L²)，平均 O(N²·L)
•	面试中常见漏点：脱口而出"O(N²)"，忘了 substring search 不是 O(1)
Level 1：KMP 替换 substring search - O(N²·L)
把 brute force 里的 in 换成 KMP，单次匹配从最坏 O(L²) 降到 O(L)。但没有解决"N 个 pattern 要轮着试"这个根本问题——每对 (text, pattern) 还是独立匹配。
按长度排序、命中早停等都是常数优化，不改复杂度。这一层主要是教学价值：让你看清"单模 vs 多模"的本质区别。
Level 2：前缀 Trie - O(N·L)
只对前缀包含有效（如 cat 是 category 的前缀）。
做法：
1.	把所有词插 trie，每个词末尾打 end-of-word 标记
2.	对每个词 w，从根按字符走
3.	走到途中遇到 end-of-word（且不是 w 自己的终点）→ w 包含某个真前缀词
复杂度：建 trie O(N·L)，每次查询 O(L)，命中早停。总 O(N·L)，达到下界。
边界：要排除"w 自己的终点"——简单做法是先建 trie 后查询，查询时记录是否还在最后一个字符。
Level 3：子串 Trie - O(N·L²)
如果要求是子串包含，需要把每个词的所有起始位置都在 trie 里走一遍。
python
for w in words:
    for start in range(len(w)):
        node = root
        for i in range(start, len(w)):
            if w[i] not in node.children:
                break
            node = node.children[w[i]]
            if node.is_end and not is_self_match(start, i, w):
                # hit
•	时间 O(N·L²)，比 brute force 的 O(N²·L²) 好一个 N 因子
•	空间 O(N·L) 存 trie
•	实现门槛低，30-50 行
•	大多数面试这一层就够了
Level 4：Aho-Corasick - O(N·L + 命中数)
多模式匹配的"最优解"。把所有词当 pattern 编译进 trie + fail 指针，每个 text 扫一次找出所有命中。详见第 3 部分。
Level 5：后缀自动机 / Generalized Suffix Tree
更高级。把所有词拼起来建 generalized suffix automaton 或 generalized suffix tree，然后对每个词查询其完整字符串是否作为子串出现在结构中（且不只来自自己）。
•	构建 O(总长度)
•	查询 O(|w|)
•	总 O(N·L)
•	但实现成本极高（200+ 行），面试基本不会要求
•	知道"这个东西存在并能解决问题"就够了
________________________________________
第 3 部分：Aho-Corasick 详解
直觉：为什么需要它
KMP 解决"1 个 pattern 在 1 个 text 里"。 当你有 K 个 pattern 都要在同一个 text 里找，KMP 跑 K 遍是 O(K·|text|)。 AC 把 K 个 pattern 编译成一个共享自动机，扫一次 text 就能找出所有命中——O(|text| + 命中数)。
它就是 KMP 的"多模式版本"。
三个组件
1.	Trie 骨架：所有 pattern 插入 trie。
2.	Fail 指针：每个节点指向"当前节点对应字符串的最长真后缀，且这个真后缀也是 trie 中某条路径的前缀"。这是 KMP failure function 在 trie 上的推广。
3.	Output 链：每个节点维护"如果走到这里，会自然命中哪些 pattern"——通过 fail 链传递。
Fail 指针定义
类比 KMP：在文本里匹配 pattern，匹配到位置 i 失败时，KMP 不回退到开头，而是跳到 pattern 内部一个聪明的位置（最长 proper border）。
AC 把这个想法搬到 trie：
•	你正沿着 trie 走 text，到了节点 v（代表已匹配的字符串 P）
•	下一个字符不在 v 的子节点里 → 不要重启，跳到 fail(v)
•	fail(v) = "P 的最长真后缀，使其在 trie 中也是某条路径的前缀"
具体例子：模式 ["he", "she", "hers"]，text 喂 "she"
•	沿 trie 走完 root → s → h → e（即 "she" 节点）
•	fail(she) = he（因为 "he" 是 "she" 的最长真后缀，且 trie 中有 "he" 这条路径）
•	这意味着：每当我们走完 "she"，应顺着 fail 链同时检查"是否在 'he' 这个 pattern 上也命中了"
•	输出 "she" 和 "he" 两个命中 
为什么是线性
关键 insight：主指针每前进 1 步，fail 跳跃总长度的均摊是 O(1)。这与 KMP 是同样的均摊论证：fail 指针只能往浅处跳（depth 严格变小），而每次主指针深入一步 depth 才 +1。所以总 fail 跳跃数 ≤ 总主指针前进数 = O(|text|)。
加上每个命中输出 O(1)，总 O(|text| + 命中数)。
构建步骤
1.	把所有 pattern 插入 trie，O(总 pattern 长度)
2.	BFS 遍历 trie，按层计算 fail 指针： 
o	第 1 层节点的 fail 全是 root
o	对节点 u 经字符 c 到子节点 v： 
	让 f = fail(u)
	沿 fail 链找到第一个有 c 子节点的 f'，则 fail(v) = f'.children[c]
	找不到则 fail(v) = root
3.	匹配阶段：单指针沿 trie 走 text，遇到无效转移走 fail，每个节点检查自身 + fail 链上的 output
工程实现要点
•	BFS 顺序（不是 DFS）保证计算 fail(v) 时 fail(u) 已就绪
•	output 链要预计算（或用懒求值），避免匹配时反复遍历
•	进阶：把 fail 链折叠成完整 DFA（goto 函数），匹配阶段每步真正 O(1)。这就是教科书里的"AC automaton 的 DFA 形式"
面试中的取舍策略
•	时间紧 → trie 子串版（每起点扫一遍）足够，O(N·L²) 在 N、L ≤ 1000 都能过
•	时间宽裕 + 面试官明确想看高阶解法 → AC
•	一开始就提 AC、说出"这是 KMP 在多模式上的推广"是加分项
•	但不要没建立简单解法就跳到 AC——会让面试官觉得你只会背高阶模板，不懂基础
________________________________________
第 4 部分：关键名词速查
名词	一句话解释
Trie / 前缀树	把字符串集合按前缀共享存储的树
KMP failure function	失配时跳到的位置，等于已匹配串的最长 proper border
Proper border	既是 string 非空前缀又是非空后缀的字符串（不含整串本身）
Aho-Corasick	Trie + fail 指针的多模式匹配自动机
Suffix array	把所有后缀字典序排序后的索引数组，O(n log n) 或 O(n) 构建
Suffix automaton	接受所有后缀的最小 DFA，O(n) 构建
Generalized suffix tree	多个串的后缀树
Z-function	每位置的"以该位置开始的最长子串等于整串前缀"的长度
Manacher	O(n) 找所有回文子串中心
Substring search 单模式	KMP / Boyer-Moore / Rabin-Karp / Crochemore-Perrin
Multi-pattern search	Aho-Corasick / Commentz-Walter / Wu-Manber
均摊分析	一系列操作总开销 / 操作数，单次最坏可能高但总和受控
________________________________________
第 5 部分：与 AI 协作的具体话术
Prompt 模板 1：澄清阶段
"我有这道题：[题面]。在动手前，请列出：(1) 题面中模糊或多解读的点；(2) 必须确认的边界条件；(3) 输入规模假设。请只列问题，不要给解法。"
最后一句很关键——防止 AI 越界给方案。
Prompt 模板 2：让 AI 验证你的复杂度
"我打算用 [算法名] 解这道题。我推导的时间复杂度是 O(...)，空间 O(...)。请审查这个推导，特别检查 [可能漏掉的开销，如 substring search 的真实代价、hash 冲突、动态扩容等]。"
明确指出潜在陷阱，AI 才会针对性检查。
Prompt 模板 3：实现阶段
"请用 Python 实现 [明确算法名，如 'Aho-Corasick automaton']。要求：(1) 显式注释每段对应算法的哪一阶段（建 trie / 计算 fail / 匹配）；(2) 处理这些 edge case：空 list、单字符词、重复词、空字符串；(3) 不引入除标准库外的依赖。"
注意：先说算法名，再说实现要求。永远不要让 AI 猜你想要什么。
Prompt 模板 4：审查阶段
"对于这段代码：[code]。请检查：(1) 时间复杂度是否真的是我预期的 O(...)？(2) 哪些 edge case 没处理？(3) 哪一行最有可能在面试中被追问？给出具体行号。"
反模式（不要这样 prompt）
•	[FAIL] "帮我写一个高效的解法"
•	[FAIL] "这道题最优解是什么？"
•	[FAIL] "请帮我做这道面试题"
•	[FAIL] "这段代码哪里可以优化？"（太开放，AI 会瞎改）
________________________________________
第 6 部分：备考刷题清单
必须熟练（trie 类）
•	LC 208 - Implement Trie
•	LC 648 - Replace Words（前缀 trie 模板题）
•	LC 720 - Longest Word in Dictionary
•	LC 642 - Design Search Autocomplete System
推荐（trie + DP / 高阶组合）
•	LC 472 - Concatenated Words
•	LC 212 - Word Search II（trie + 回溯，经典）
•	LC 1268 - Search Suggestions System
KMP 类
•	LC 28 - Implement strStr
•	LC 459 - Repeated Substring Pattern
•	LC 1392 - Longest Happy Prefix（KMP failure function 直接应用）
•	LC 214 - Shortest Palindrome
Aho-Corasick（罕见但出现就是难题）
•	洛谷 P3796 - AC 自动机简单版
•	洛谷 P5357 - AC 自动机二次加强版（fail 树 DP）
后缀结构（高阶，了解即可）
•	LC 1044 - Longest Duplicate Substring
•	LC 1923 - Longest Common Subpath
________________________________________
第 7 部分：本题"完美面试回答"模板
把前面 6 部分的内容串起来，下面是面试中可以直接套用的话术节奏：
澄清阶段："好的。先确认几个问题：'包含'是指子串还是前缀？示例 [category, cat] 不能区分。词可以重复吗？输出是只要包含的 word 还是 (word, contained) 对？输入规模大概多少？"
下界阶段："让我先想下界。我们必须读完所有词，所以是 Ω(N·L)。这告诉我目标是线性。"
谱系阶段："解法谱系大致是这样：
Brute force O(N²·L²) 因为每个 substring search 最坏 O(L²)。
一个直接优化是把 substring search 换成 KMP，得 O(N²·L)，但根本问题是 N 个 pattern 还在轮着试——这是经典多模匹配场景，单模式工具治标不治本。
Trie 路线：所有词建 trie，每个词查询时检查路径上是否提前命中 end-of-word。前缀版直接 O(N·L)，子串版每个起点试一遍是 O(N·L²)。
最优是 Aho-Corasick，O(N·L + 命中数)，原理是 trie + KMP 风格的 fail 指针，把不同 pattern 的部分匹配信息共享。"
选型阶段："时间所限，我先实现 trie 子串版，确定逻辑正确后，如果时间允许我们升级到 AC。可以吗？"
实现阶段：（你画 trie 结构，列边界条件，再让 AI 写代码）
验证阶段：（手算一两个测试用例，跑边界）
这套话术覆盖了：澄清 → 下界 → 谱系 → 沟通 → 取舍。即使最后没时间写到 AC，过程已经满分。









7. Card Game:
AI 辅助 coding：card game
第一问：unittest一开始失败，原因是有的牌不是从桌上现有的牌里抽的，需要debug抽牌的method，确保三张牌都来自桌上的牌再抽。
第二问：写一个naive的抽牌策略。楼主说原始策略可以像3Sum一样，每次抽任意三张加起来为15的牌，保证那一轮得分即可，先不保证总分最优。
第三问：measure策略有多优化。楼主说可以simulate抽牌游戏若干次，看多少百分比的局能拿满分。面试官说可以。上述策略大约在~40%的情况下能拿满分。
第四问：让优化策略。楼主说可以backtrack，尝试所有抽牌方式，选择总分最高的那一种。改进后约 90%的牌局可以得满分。
撲克牌四花色每個花色(1~9)總共36張牌，初始檯面上有16張牌(隨機從36張生成)，三張牌湊到15點成對獲得15分(像是不同花色的5 三張 or 9 + 4 + 2)，拿了三張後會補牌直到沒有牌或檯面上不能再湊對。完美條件下能湊12對 (15 * 12 = 180 分)。題目有點亂code 很大所以花了十幾分鐘大概理解
1. 修UT，面試官人很好跟我說UT(unit test)第幾行報錯，本來以為是在UT裡改但其實是Main 少了一個if else，看懂code就挺簡單的
2. 寫一個拿牌的strategy, 我內心暗想要dp，怕AI不靠譜等很久，先提 3 sum的greedy方法寫了一個，考官說可以。寫完要我run 幾次觀察得分
3. 要我寫一個UT 跑一百次遊戲看可以拿幾次滿分(180)。讓AI generate UT，然後在自己稍微改下。結果是 20/100
4. 考官問能不能進步我提DP只剩下十分鐘就讓AI生成了，沒想到一下就跑出來了code有150多行看了一眼沒認真validate就貼進去跑test結果過了，100次遊戲60次滿分。考官讓我解釋dp的思路，嗑嗑巴巴解釋了一下。考官看時間要到了最後問一下有沒有完美strategy每次都能拿到滿分，我說會沒有因為牌是隨機生成，如果初始隨機檯面上只有4 * 9, 4* 8, 4*7, 4* 6那就直接game over了
Q: 想问下，对于拿牌的strategy implementation, input 是上帝视角知道整个发牌顺序吗？ 还是只知道台面上的牌？guess是后一种input？
A: 發牌順序完全隨機，input是台面上16張牌但知道牌庫就是36張牌（1-9×4）
不太確定你說的guess是什麼遊戲過程是這樣的：台面上16張牌，選三張湊成十五，隨機從牌庫裡補牌三張，一直循環到所有牌拿完或game over（無法組成15）
Run的過程就是一直呼叫strategy，判斷game over or perfect game已經寫好了
Q:扑克牌这道题有一个很重要的条件麻烦确认下：
能否选择重复的牌， 例如 5，5，5 或者1， 7， 7。还是三张牌必须要不同， 例如1，5，9， 或者 2， 6， 7 等等。
A:我寫的時候沒有考慮數字不能重複的情況，所以我寫的是前面那種，但我建議你跟面試官確認




Card Game (Sum-15) · 复习卡
澄清四问（开场必问）
1. 数值能否重复？  (5,5,5) / (1,7,7) 是否合法
2. 花色须互异？    选中 3 张物理牌是否要不同花色
3. 输入信息？      看得到台面 + 已知牌库 multiset；下次补牌随机
4. 终止条件？      台面无 valid triple → game over（不必等牌库空）
关键常数
36 张 = 1..9 各 4 张   |   初始台面 16 张   |   完美局 = 12 对 = 180 分
合法 rank multiset 13 种：
  (1,5,9)(1,6,8)(1,7,7)
  (2,4,9)(2,5,8)(2,6,7)
  (3,3,9)(3,4,8)(3,5,7)(3,6,6)
  (4,4,7)(4,5,6)
  (5,5,5)
分级解法（讲得出 = 拿分）
Tier	思路	Perfect 率	面试用途
1 Naive Greedy	扫到第一个 sum=15 就拿	~20–40%	暖场 / baseline
2 Heuristic Greedy	优先拿"瓶颈 rank"(已堆 4 张) 和"不灵活 rank"(1/9)	~50–60%	性价比之王
3 Table-only Backtrack	当前台面 DFS + memo，忽略补牌	~60%	楼主 AI 写的版本
4 Monte Carlo Rollout	每个候选 triple 跑 K 次随机 rollout 取均值	~80%+	首选实战方案
5 真·Expectimax DP	state=(table,deck)，对超几何分布求期望	最优	只口述不写
Tier 5 DP 思路（口述模板）
State: (table[1..9], deck[1..9])  两个 9-tuple
Bellman:
  V(t,d) = 0                       if no valid triple in t
  V(t,d) = max_triple { 15 + E_draw[ V(t-triple+draw, d-draw) ] }
  draw ~ 多元超几何(d, size=3)
变体:
  目标=期望分 → 上式
  目标=满分概率 → 把 15+ 换成乘法递推, 边界 taken 满 = 1
State 空间 ~10⁶ reachable, Python 慢, C++ 可
→ 实战取 MC rollout 做采样近似
Implementation Pitfalls
 def f(x, memo={})            # 默认参数共享坑
 @lru_cache(maxsize=None)     # state 是 tuple, 函数纯 → 一行搞定
 memo 作参数传                 # 无回退需求, 全局共享即可
 rank-level DP + 花色 filter 单独函数  # 对称性 + 灵活性
Meta-Prompt（AI 协作四步）
1. CLARIFY  先问澄清四问, 不动键盘
2. TIER     口头报 Tier 1→5 的爬升路线, 选 Tier 4 实战
3. NARRATE  AI 出代码 → 你读 → 对面试官讲"这段在做 X 因为 Y" → 再 paste
4. BUFFER   留 5 分钟 validate + 解释; 宁可 Tier 2 讲透, 不要 Tier 5 贴爆
一句话防呆
"看了一眼没认真 validate 就贴进去"是 AI 面试最大的失分点。算法选你 hold 得住的那一档。
备考迁移
3Sum / subset-sum / partition-k-subsets   ← 枚举骨架
Backtrack + memoization 模板               ← 30 行内手写
Monte Carlo rollout / MCTS 入门            ← 优化题不一定要真最优
State 压缩成 tuple/frozenset               ← 让 lru_cache 工作
平时刷题强制"先口述再让 AI 写"             ← 肌肉记忆

















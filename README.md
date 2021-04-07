# 实体-关系抽取模型

基于标注模型，百度SAOKE语料库实现的关系抽取模型。

## 使用简介

### 依赖环境

requirements.txt 存储该模型所需依赖包。

使用 `pip install -r requirements.txt` 安装所有依赖环境。

### 输入

将带抽取关系的句子，每句一行存放于项目根目录的`input.txt`文件中。

### 标注、抽取

命令行输入`./ie.sh tag` 进行标注。

之后命令行输入`./ie.sh ie` 进行分组，并储存结果。

结果储存于`facts.json` 文件中。

### 结果格式

```
[   {   'object': '_',
        'place': '_',
        'predict': '不服一审判决',
        'qualifier': '_',
        'subject': ['泽文公司'],
        'time': '_'},
    {   'object': '_',
        'place': '_',
        'predict': '提起上诉',
        'qualifier': '_',
        'subject': '_',
        'time': '1997年6月28日'}]
```

每个句子生成一个list，每个list包含0或多个dictionary，每个dictionary代表每个六元祖。六元祖包含主语、谓语、宾语、时间、地点、约束条件。

## 算法简介

抽取的流程分为两部分

1. 对一个句子做标注
2. 根据标注来提取三元组

### 句子标注

我们首先需要把百度SAOKE数据转换为我们需要的形式。我们根据一系列规则，将SAOKE数据转化为标注问题的训练数据。这里给出一个例子。

```
{"natural": "赞比亚在2014年前列为不发达国家而不是发展中国家。", 
  "logic": [
      { "predicate": "列为",
        "qualifier": "_",
        "object": ["不发达国家"],
        "place": "_",
        "time": "在2014年前",
        "subject": "赞比亚"},

      { "predicate": "不是",
        "qualifier": "_",
        "object": ["发展中国家"],
        "place": "_",
        "time": "在2014年前",
        "subject": "赞比亚"}
      ]
}
```
我们给每个部分分配一个TAG，predicate为P，qualifier为Q，object为O，time为T。接下来使用LSTM+CRF模型训练，以字为单位，character level的向量，向量随机初始化。

### 关系分组

使用训练之后的模型标注输入的句子，得到句子对应的TAG序列。之后的工作是根据TAG序列得到一系列三元组。这里我提出一个GROUP算法，将TAG序列转化为三元组。

具体过程如下：

1. 若在一个小句子中（小句子指句子根据标点符号分割后的基本单元）同时出现谓语predicate和主语subject、宾语object其中之一则将其匹配为一个三元组。
2. 建立滑动窗口。
3. 滑动窗口内，若出现谓语predicate和主语subject、宾语object其中之一，或同时出现，则将它们匹配为一个三元组。

这里举一个例子：
```
泽文公司不服一审判决，于1997年6月28日提起上诉。
SSSSPPPPPPNNTTTTTTTTTTPPPPN

分组后结果：
[{"subject": ["泽文公司"], "predicate": "不服一审判决", "object": "_", "time": "_", "place": "_", "qualifier": "_"}, {"subject": ["泽文公司"], "predicate": "提起上诉", "object": "_", "time": "1997年6月28日", "place": "_", "qualifier": "_"}]
```


## Server: WEB_API的使用

web_api 工作在：
`host: 0.0.0.0:8010`

### 使用方法：

#### 输入

GET方法传递待抽取的句子／片段：
`localhost:8010\ie?s=我爱吃苹果`

**注意新添加了POST方法接受待抽取文本。**

或是

```
localhost:8010\ie?s=泽文公司不服一审判决，于1997年6月28日提起上诉。|泽文公司系设在青岛保税区的日商独资企业。|国家工商行政管理局为其颁发的营业执照中载明，泽文公司的经营范围是：国际贸易、转口贸易、生产加工、汽车零配件。
```

若是片段，则后台会根据符号`|`分割成单句，再进行抽取。
**POST方法，根据换行符`\n`来分割成单句。**

#### 输出

每个dic代表一个关系，是一个六元组。每个句子可能会抽取出多条关系，由一个list包含这多个dic。最外边一个list包含所有的句子。

例如，

**单句**

```
[
  [
    {
      "object": [
        "苹果"
      ], 
      "place": "_", 
      "predicate": "爱吃X", 
      "qualifier": "_", 
      "subject": [
        "我"
      ], 
      "time": "_"
    }
  ]
]
```

**段落**

```
[
  [
    {
      "object": "_", 
      "place": "_", 
      "predicate": "不服一审判决", 
      "qualifier": "_", 
      "subject": [
        "泽文公司"
      ], 
      "time": "_"
    }, 
    {
      "object": "_", 
      "place": "_", 
      "predicate": "提起上诉", 
      "qualifier": "_", 
      "subject": [
        "泽文公司"
      ], 
      "time": "1997年6月28日"
    }
  ], 
  [
    {
      "object": [
        "青岛保税区的日商独资企业"
      ], 
      "place": "_", 
      "predicate": "系设在X", 
      "qualifier": "_", 
      "subject": [
        "泽文公司"
      ], 
      "time": "_"
    }
  ], 
  [
    {
      "object": [
        "营业执照中载明，泽文公司的经营范围"
      ], 
      "place": "_", 
      "predicate": "为其颁发", 
      "qualifier": "_", 
      "subject": [
        "国家工商行政管理局"
      ], 
      "time": "_"
    }
  ]
]
```


# Web Demo

使用stramlit框架的构建的web demo演示页面。

演示页面包含了json样式的输出和表格形式的输出，并且有根据抽取的三元组结果产出知识图谱的api.

![demo界面的示意图](https://github.com/liyucheng09/IE_with_tag_mechanism/blob/master/img/demo.png)
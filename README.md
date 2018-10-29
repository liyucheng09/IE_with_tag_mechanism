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


## Server: WEB_API的使用

web_api 工作在：
`host: 0.0.0.0:8010`

### 使用方法：

#### 输入

GET方法传递待抽取的句子／片段：
`localhost:8010\ie?s=我爱吃苹果`

或是

```
localhost:8010\ie?s=泽文公司不服一审判决，于1997年6月28日提起上诉。|泽文公司系设在青岛保税区的日商独资企业。|国家工商行政管理局为其颁发的营业执照中载明，泽文公司的经营范围是：国际贸易、转口贸易、生产加工、汽车零配件。
```

若是片段，则后台会根据符号`|`分割成单句，再进行抽取。

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

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
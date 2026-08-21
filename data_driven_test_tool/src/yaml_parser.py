# -*- coding: utf-8 -*-
"""
手写轻量 YAML 解析器。

不依赖 PyYAML、pytest-yaml 等第三方 YAML 库。
仅覆盖本工具用例文件所需的子集：
- 字典、列表、缩进嵌套
- 字符串、整数、浮点数、布尔、null
- 单行注释（#）
- 单引号 / 双引号字符串
"""


class YamlParseError(ValueError):
    """YAML 语法不符合本解析器支持范围时抛出。"""


class SimpleYamlParser:
    """按缩进解析 YAML 文档的轻量实现。"""

    def parse(self, text):
        """
        将 YAML 文本解析为 Python 对象（dict / list / 标量）。

        :param text: YAML 文件全文
        :return: 解析后的根对象
        """
        if text is None:
            raise YamlParseError("YAML 内容为空")

        # 统一换行，去掉 BOM，再拆成带行号的有效行
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        if normalized.startswith("\ufeff"):
            normalized = normalized[1:]

        lines = []
        for lineno, raw in enumerate(normalized.split("\n"), start=1):
            stripped_comment = self._strip_comment(raw)
            if stripped_comment.strip() == "":
                continue
            indent = self._count_indent(stripped_comment)
            content = stripped_comment.rstrip()
            # 去掉左侧缩进空格，保留内容本身
            content = content[indent:]
            lines.append((lineno, indent, content))

        if not lines:
            return {}

        value, next_index = self._parse_block(lines, 0, lines[0][1])
        if next_index != len(lines):
            leftover_line = lines[next_index][0]
            raise YamlParseError("第 %s 行存在无法归属的内容" % leftover_line)
        return value

    def _count_indent(self, line):
        """统计行首空格数。禁止使用 Tab，避免缩进歧义。"""
        indent = 0
        for char in line:
            if char == " ":
                indent += 1
            elif char == "\t":
                raise YamlParseError("不支持 Tab 缩进，请改用空格")
            else:
                break
        return indent

    def _strip_comment(self, line):
        """
        去掉未处于引号内的 # 注释。
        例如：name: demo  # 说明  ->  name: demo
        """
        in_single = False
        in_double = False
        result = []
        for char in line:
            if char == "'" and not in_double:
                in_single = not in_single
                result.append(char)
            elif char == '"' and not in_single:
                in_double = not in_double
                result.append(char)
            elif char == "#" and not in_single and not in_double:
                break
            else:
                result.append(char)
        return "".join(result)

    def _parse_block(self, lines, index, min_indent):
        """
        从 lines[index] 开始解析同一缩进层级的块。
        根据首条有效内容判断是列表还是字典。
        """
        if index >= len(lines):
            return None, index

        _, indent, content = lines[index]
        if indent < min_indent:
            return None, index

        if content.startswith("- ") or content == "-":
            return self._parse_list(lines, index, indent)
        return self._parse_mapping(lines, index, indent)

    def _parse_list(self, lines, index, list_indent):
        """解析同一缩进层级的 YAML 列表。"""
        items = []
        while index < len(lines):
            lineno, indent, content = lines[index]
            if indent < list_indent:
                break
            if indent > list_indent:
                raise YamlParseError("第 %s 行列表缩进不一致" % lineno)
            if not (content.startswith("- ") or content == "-"):
                raise YamlParseError("第 %s 行期望列表项（以 - 开头）" % lineno)

            item_text = content[1:].strip()
            index += 1

            if item_text == "":
                # 纯 "-" 后面跟嵌套块
                nested, index = self._parse_nested(lines, index, list_indent)
                items.append({} if nested is None else nested)
                continue

            if self._looks_like_key_value(item_text):
                # 形如 "- name: 登录" ：当前行是字典的第一个键
                # YAML 中 "- " 占两个字符，后续兄弟字段通常与键名对齐
                item_key_indent = list_indent + 2
                key, raw_value = self._split_key_value(item_text, lineno)
                first_map = {}
                if raw_value == "":
                    nested, index = self._parse_nested(lines, index, item_key_indent)
                    first_map[key] = {} if nested is None else nested
                else:
                    first_map[key] = self._parse_scalar(raw_value)

                extra, index = self._collect_mapping_rest(lines, index, item_key_indent)
                first_map.update(extra)
                items.append(first_map)
            else:
                # 形如 "- hello" 的标量列表项，不允许后面再挂同级嵌套键
                items.append(self._parse_scalar(item_text))
        return items, index

    def _collect_mapping_rest(self, lines, index, item_key_indent):
        """收集列表项中与首个键对齐的其余字典字段。"""
        if index >= len(lines):
            return {}, index
        _, indent, content = lines[index]
        if indent < item_key_indent:
            return {}, index
        if content.startswith("- ") or content == "-":
            return {}, index
        return self._parse_mapping(lines, index, indent)

    def _parse_mapping(self, lines, index, map_indent):
        """解析同一缩进层级的 YAML 字典。"""
        mapping = {}
        while index < len(lines):
            lineno, indent, content = lines[index]
            if indent < map_indent:
                break
            if indent > map_indent:
                raise YamlParseError("第 %s 行字典缩进不一致" % lineno)
            if content.startswith("- ") or content == "-":
                raise YamlParseError("第 %s 行在字典中出现了列表项" % lineno)

            key, raw_value = self._split_key_value(content, lineno)
            index += 1
            if raw_value == "":
                nested, index = self._parse_nested(lines, index, indent)
                mapping[key] = {} if nested is None else nested
            else:
                mapping[key] = self._parse_scalar(raw_value)
        return mapping, index

    def _parse_nested(self, lines, index, parent_indent):
        """解析比父节点缩进更深的子节点；没有子节点则返回 None。"""
        if index >= len(lines):
            return None, index
        _, indent, _ = lines[index]
        if indent <= parent_indent:
            return None, index
        return self._parse_block(lines, index, indent)

    def _looks_like_key_value(self, text):
        """判断一段文本是否为 key: value 形式。"""
        return self._find_key_separator(text) is not None

    def _split_key_value(self, text, lineno):
        """把 'key: value' 拆成键和原始值字符串。"""
        pos = self._find_key_separator(text)
        if pos is None:
            raise YamlParseError("第 %s 行缺少冒号，无法解析为键值对：%s" % (lineno, text))
        key = text[:pos].strip()
        value = text[pos + 1 :].strip()
        if key == "":
            raise YamlParseError("第 %s 行键名为空" % lineno)
        return key, value

    def _find_key_separator(self, text):
        """在未引号区域内查找第一个 ': ' 或行尾 ':'。"""
        in_single = False
        in_double = False
        for i, char in enumerate(text):
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == ":" and not in_single and not in_double:
                # 标准 YAML：冒号后应为空格，或位于行尾表示嵌套块
                if i == len(text) - 1:
                    return i
                if text[i + 1] == " ":
                    return i
        return None

    def _parse_scalar(self, raw):
        """把标量文本转成 Python 基本类型。"""
        if raw == "~" or raw.lower() in ("null", "none"):
            return None
        if raw.lower() == "true":
            return True
        if raw.lower() == "false":
            return False

        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
            quote = raw[0]
            inner = raw[1:-1]
            if quote == '"':
                inner = (
                    inner.replace("\\n", "\n")
                    .replace("\\t", "\t")
                    .replace('\\"', '"')
                    .replace("\\\\", "\\")
                )
            return inner

        # 整数
        if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
            return int(raw)

        # 浮点数
        try:
            if "." in raw or "e" in raw.lower():
                return float(raw)
        except ValueError:
            pass

        return raw


def load_yaml_file(path):
    """
    读取 UTF-8 YAML 文件并解析。

    :param path: 文件路径
    :return: Python 对象
    """
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    return SimpleYamlParser().parse(text)

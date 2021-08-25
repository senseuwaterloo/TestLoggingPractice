import os
import re
import subprocess
from pathlib import Path
from lxml import etree

from Models.Log import LogCallerType, LogVerbosityType
from Utils import FileUtil, BashUtil

NS_MAP = {"src": "http://www.srcML.org/srcML/src"}


def get_logging_calls_xml_of_repo(repo_path: str):
    java_file_list = FileUtil.get_all_java_files(repo_path)
    total_result, total_assert_result, total_print_result, total_log_result = [], [], [], []
    test_result, test_assert_result, test_print_result, test_log_result = [], [], [], []
    production_result, production_assert_result, production_print_result, production_log_result = [], [], [], []

    total_trace, total_debug, total_info, total_warn, total_error = 0, 0, 0, 0, 0
    test_trace, test_debug, test_info, test_warn, test_error = 0, 0, 0, 0, 0
    production_trace, production_debug, production_info, production_warn, production_error = 0, 0, 0, 0, 0


    for java_path in java_file_list:
        total_calls, assert_calls, print_calls, log_calls = get_logging_calls_xml_of_file(str(java_path))
        trace_num, debug_num, info_num, warn_num, error_num = get_log_verbosity_num(total_calls)
        total_trace += trace_num
        total_debug += debug_num
        total_info += info_num
        total_warn += warn_num
        total_error += error_num
        total_result.extend(total_calls)
        total_assert_result.extend(assert_calls)
        total_print_result.extend(print_calls)
        total_log_result.extend(log_calls)
        if FileUtil.is_test_file(str(java_path)):
            test_trace += trace_num
            test_debug += debug_num
            test_info += info_num
            test_warn += warn_num
            test_error += error_num
            test_result.extend(total_calls)
            test_assert_result.extend(assert_calls)
            test_print_result.extend(print_calls)
            test_log_result.extend(log_calls)
        else:
            production_trace += trace_num
            production_debug += debug_num
            production_info += info_num
            production_warn += warn_num
            production_error += error_num
            production_result.extend(total_calls)
            production_assert_result.extend(assert_calls)
            production_print_result.extend(print_calls)
            production_log_result.extend(log_calls)

    return total_result, total_assert_result, total_print_result, total_log_result, \
        test_result, test_assert_result, test_print_result, test_log_result, \
        production_result, production_assert_result, production_print_result, production_log_result, \
        [total_trace, total_debug, total_info, total_warn, total_error], \
        [test_trace, test_debug, test_info, test_warn, test_error], \
        [production_trace, production_debug, production_info, production_warn, production_error]


def get_logging_calls_xml_of_file(file_path: str):
    methods = get_methods_of_file(file_path)
    total_result = []
    assert_result = []
    print_result = []
    log_result = []
    for method in methods:
        method_str = b'<root>' + etree.tostring(method) + b'</root>'
        method = etree.fromstring(method_str, etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
        total_calls, assert_calls, print_calls, log_calls = get_logging_calls_xml_of_method(method)
        total_result.extend(total_calls)
        assert_result.extend(assert_calls)
        print_result.extend(print_calls)
        log_result.extend(log_calls)

    return total_result, assert_result, print_result, log_result


def get_methods_of_file(file_path: str):
    xml_name = FileUtil.generate_random_file_name_with_extension('xml')
    methods = []
    xml_p = None
    try:
        BashUtil.run("srcml '{}' -o {}".format(file_path, xml_name))
        xml_p = Path(xml_name)
        xml_bytes = xml_p.read_bytes()
        methods = get_methods_of_xml_bytes(xml_bytes)
    finally:
        xml_p.unlink()
        return methods


def get_methods_of_xml_bytes(xml_bytes):
    if xml_bytes is not None:
        parser = etree.XMLParser(huge_tree=True, encoding='utf-8', ns_clean=True, recover=True)
        xml_object = etree.fromstring(xml_bytes, parser=parser)
        methods = xml_object.xpath('//src:unit//src:class[src:specifier]/src:block/src:function', namespaces=NS_MAP)
        return methods
    else:
        return []


def get_logging_calls_xml_of_method(method_xml):
    total_result = []
    assert_result = []
    print_result = []
    log_result = []
    method_calls_xml = get_calls_in_method(method_xml)
    for method_call_xml in method_calls_xml:
        if _is_logging_call(method_call_xml):
            total_result.append(method_call_xml)
            call_type = get_log_call_type(method_call_xml)
            if call_type == LogCallerType.ASSERT_CALL:
                assert_result.append(method_call_xml)
            elif call_type == LogCallerType.PRINT_CALL:
                print_result.append(method_call_xml)
            else:
                log_result.append(method_call_xml)

    return total_result, assert_result, print_result, log_result


def get_calls_in_method(method_xml):
    # TODO: Get first call directly
    xpath_str = '//src:expr_stmt/src:expr/*[1]'
    method_calls_xml = method_xml.xpath(xpath_str, namespaces=NS_MAP)
    result_method_calls_xml = method_calls_xml
    for item in method_calls_xml:
        if not etree.tostring(item).decode('utf-8').startswith('<call'):
            result_method_calls_xml.remove(item)
    return result_method_calls_xml


def get_call_literal_type(method_call_xml):
    argument_xpath = './src:argument_list/src:argument'
    arguments = method_call_xml.xpath(argument_xpath, namespaces=NS_MAP)

    literal_type_xpath = './src:expr/src:literal/@type'

    result = []

    if len(arguments) == 0:
        return result

    for index in range(0, len(arguments)):
        argument = arguments[index]
        text = argument.xpath(literal_type_xpath, namespaces=NS_MAP)
        result.append(text)

    return result

def _is_logging_call(method_call_xml):
    if is_argument_none(method_call_xml):
        return False

    method_call_name = get_method_call_name(method_call_xml)

    level_name = None
    if '.' in method_call_name:
        caller_name = method_call_name.rsplit('.', 1)[:-1][0]
        level_name = method_call_name.rsplit('.', 1)[-1:][0]
    else:
        caller_name = method_call_name

    filter_assert_caller_regex = '^(assertArrayEquals|assertEquals|assertFalse|assertTrue|assertNotNull|assertNull|assertNotSame|assertSame|assertThat)$'
    p = re.compile(filter_assert_caller_regex, re.I)
    m = p.match(caller_name)
    if m is not None:
        method_call_literal_type_list = get_call_literal_type(method_call_xml)
        if len(method_call_literal_type_list) > 0 and ['string'] in method_call_literal_type_list:
            return True

    filter_caller_regex = r'.*?(log|logger|(system\.out)|(system\.err)|timber).*'
    p = re.compile(filter_caller_regex, re.I)
    m = p.match(caller_name)
    if m is None:
        return False

    filter_caller_black_regex = '.*?(dialog|login|logout|loggedin|loggedout|catalog|logical|blog|logo|logic|log4j|containerlog|logdir|setLogAggCheckIntervalMsecs).*'
    p = re.compile(filter_caller_black_regex, re.I)
    m = p.match(caller_name)
    if m is not None:
        return False

    if level_name is not None:
        filter_level_white_regex = '^(w|e|v|i|d|wtf|warn|warning|error|verbose|info|debug|severe|fine|fatal|trace|print|printf|println|log)$'
        p = re.compile(filter_level_white_regex, re.I)
        m = p.match(level_name)
        if m is None:
            return False

    return True


def get_log_call_type(method_call_xml):
    method_call_name = get_method_call_name(method_call_xml)
    level_name = None
    if '.' in method_call_name:
        caller_name = method_call_name.rsplit('.', 1)[:-1][0]
        level_name = method_call_name.rsplit('.', 1)[-1:][0]
    else:
        caller_name = method_call_name


    # assert_call_list = ['assertarrayequals', 'assertequals', 'assertfalse', 'asserttrue', 'assertnotnull', 'assertnull',
    #                     'assertnotsame', 'assertsame', 'assertthat']
    # print_call_list = ['system.out', 'system.err']
    filter_assert_caller_regex = '^(assertArrayEquals|assertEquals|assertFalse|assertTrue|assertNotNull|assertNull|assertNotSame|assertSame|assertThat)$'
    filter_print_caller_regex = '^(print|printf|println)$'
    # lowercase_method_call_name = method_call_name.lower()
    assert_p = re.compile(filter_assert_caller_regex, re.I)
    assert_m = assert_p.match(caller_name)
    print_p = re.compile(filter_print_caller_regex, re.I)
    if level_name is not None:
        print_m = print_p.match(level_name)
    else:
        print_m = None

    # print(lowercase_method_call_name)
    if assert_m is not None:
        return LogCallerType.ASSERT_CALL
    elif print_m is not None:
        return LogCallerType.PRINT_CALL
    else:
        return LogCallerType.LOG_CALL


def is_argument_none(method_xml):
    arguments_xpath = './src:argument_list/src:argument'
    arguments = method_xml.xpath(arguments_xpath, namespaces=NS_MAP)
    if len(arguments) == 0:
        return True
    else:
        return False


# e.g. get log.warn
def get_method_call_name(method_call_xml):
    method_call_name = ''
    call_with_operator_xpath_str = 'src:name//*'
    call_without_operator_xpath_str = 'src:name'
    method_call_name_xml = method_call_xml.xpath(call_with_operator_xpath_str, namespaces=NS_MAP)
    if len(method_call_name_xml) == 0:
        method_call_name_xml = method_call_xml.xpath(call_without_operator_xpath_str, namespaces=NS_MAP)
    for item in method_call_name_xml:
        if item.text is not None:
            method_call_name += item.text
    return method_call_name


def generate_java_file_of_blob(file_blob):
    java_name = FileUtil.generate_random_file_name_with_extension('java')
    java_p = Path(java_name)
    java_p.write_bytes(file_blob.data_stream.read())
    return str(java_p.resolve())


def get_methods_of_java_blob(file_blob):
    xml_bytes = get_xml_bytes_of_java(file_blob)
    methods = get_methods_of_xml_bytes(xml_bytes)
    return methods


def get_xml_bytes_of_java(file_blob):
    fifo_name = FileUtil.generate_random_file_name_with_extension('java')
    os.mkfifo(fifo_name)

    try:
        process = subprocess.Popen(['srcml', fifo_name], stdout=subprocess.PIPE)
        with open(fifo_name, 'wb') as f:
            f.write(file_blob.data_stream.read())
        output = process.stdout.read()
    finally:
        os.remove(fifo_name)

    return output


def get_method_full_signature(method_xml):
    signature = get_method_signature(method_xml)
    return signature[0] + signature[1]


def get_method_signature(method_xml):
    name_xpath = '//src:function/src:name'
    parameters_xpath = '//src:function/src:parameter_list/src:parameter/src:decl/src:type/src:name'
    parameters_element = method_xml.xpath(name_xpath, namespaces=NS_MAP)
    if parameters_element is not None and len(parameters_element) > 0:
        method_name = parameters_element[0]
        method_name_str = method_name.text
        parameters = method_xml.xpath(parameters_xpath, namespaces=NS_MAP)
        parameters_str = get_flatten_text_of_parameter(parameters)
        parameters_str = parameters_str[0:-1]
        parameters_str = '(' + parameters_str + ')'

        return method_name_str, parameters_str
    else:
        return '', ''


def get_flatten_text_of_parameter(xml):
    result = ''
    if not isinstance(xml, list):
        if len(xml) == 0:
            result = result + xml.text + ','
        else:
            for item in xml:
                result = result + get_flatten_text_of_parameter(item)
    else:
        for item in xml:
            result = result + get_flatten_text_of_parameter(item)
    return result


def get_flattern_text(xml):
    result = ''
    if not isinstance(xml, list):
        if len(xml) == 0:
            result = result + xml.text
        else:
            for item in xml:
                result = result + get_flattern_text(item)
    else:
        for item in xml:
            result = result + get_flattern_text(item)
    return result


def transform_xml_str_to_code(xml_str):
    pre_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><unit xmlns="http://www.srcML.org/srcML/src" revision="0.9.5" language="Java" filename="code_temp.java">'
    xml_str = pre_str + xml_str + '</unit>'
    fifo_name = FileUtil.generate_random_file_name_with_extension('xml')
    os.mkfifo(fifo_name)

    try:
        process = subprocess.Popen(['srcml', fifo_name], stdout=subprocess.PIPE)
        with open(fifo_name, 'w') as f:
            f.write(xml_str)
        output = process.stdout.read()
    finally:
        os.remove(fifo_name)
    return str(output)[2:-1]


def get_logging_argument(method_xml):
    argument_xpath = './src:argument_list/src:argument'
    arguments = method_xml.xpath(argument_xpath, namespaces=NS_MAP)

    text_xpath = './src:expr/src:literal'
    var_xpath = './src:expr/src:name'
    sim_xpath = './src:expr/src:call'

    result = []

    if len(arguments) == 0:
        result.append(([], [], []))

    for index in range(0, len(arguments)):
        argument = arguments[index]
        text = argument.xpath(text_xpath, namespaces=NS_MAP)
        var = argument.xpath(var_xpath, namespaces=NS_MAP)
        sim = argument.xpath(sim_xpath, namespaces=NS_MAP)
        result.append((text, var, sim))

    return result


def compare_method_signature(method_xml_a, method_xml_b):
    a_method_signature = get_method_signature(method_xml_a)
    b_method_signature = get_method_signature(method_xml_b)
    is_same_name = True if a_method_signature[0] == b_method_signature[0] else False
    is_same_parameters = True if a_method_signature[1] == b_method_signature[1] else False
    return is_same_name, is_same_parameters


def get_method_block_content(method_xml):
    content_xpath = '//src:function/src:block'
    content_xml = method_xml.xpath(content_xpath, namespaces=NS_MAP)[0]
    return content_xml


def generate_java_file_of_str(text: str):
    java_name = FileUtil.generate_random_file_name_with_extension('java')
    java_p = Path(java_name)
    java_p.open('w').write(text)
    return str(java_p.resolve())


def transform_log_str_to_xml_obj(code_str):
    code_str_components = code_str.split('(', 1)
    caller_method = code_str_components[0]
    caller_method = caller_method.replace('\\n', '').replace('\\t', '').replace('\\r', '')
    formatted_code_str = caller_method + '(' + code_str_components[1]
    java_file_path = generate_java_file_of_str(formatted_code_str)
    xml_name = FileUtil.generate_random_file_name_with_extension('xml')
    methods = []
    xml_p = None
    # xml_object = None
    try:
        BashUtil.run("srcml '{}' -o {}".format(java_file_path, xml_name))
        xml_p = Path(xml_name)
        xml_bytes = xml_p.read_bytes()
        parser = etree.XMLParser(huge_tree=True, encoding='utf-8', ns_clean=True, recover=True)
        xml_object = etree.fromstring(xml_bytes, parser=parser)
        # print(xml_bytes.decode('utf-8'))
        methods = get_method_calls(xml_object)
    finally:
        xml_p.unlink()
        java_p = Path(java_file_path)
        java_p.unlink()
        if len(methods) > 0:
            return methods[0]
        else:
            return None
        # return xml_object
        # if len(methods) > 0:
        #     return methods[0]
        # else:
        #     return None


def get_method_calls(method_xml):
    # TODO: Get first call directly
    xpath_str = '//src:expr/*[1]'
    method_calls_xml = method_xml.xpath(xpath_str, namespaces=NS_MAP)
    # print('in get_method_calls')
    # print(method_calls_xml)
    result_method_calls_xml = method_calls_xml
    for item in method_calls_xml:
        if not etree.tostring(item).decode('utf-8').startswith('<call'):
            result_method_calls_xml.remove(item)
    return result_method_calls_xml


def get_all_text_str_in_call(method_xml):
    argument_xpath = './src:argument_list/src:argument'
    arguments = method_xml.xpath(argument_xpath, namespaces=NS_MAP)
    text_xpath = './src:expr/src:literal'

    result = []
    for index in range(0, len(arguments)):
        argument = arguments[index]
        texts = argument.xpath(text_xpath, namespaces=NS_MAP)
        for text in texts:
            result.append(text.text)

    return result


def get_all_var_str_in_call(method_xml):
    argument_xpath = './src:argument_list/src:argument'
    arguments = method_xml.xpath(argument_xpath, namespaces=NS_MAP)

    var_xpath = './src:expr/src:name'
    sim_xpath = './src:expr/src:call'

    result = []
    for index in range(0, len(arguments)):
        argument = arguments[index]
        method_vars = argument.xpath(var_xpath, namespaces=NS_MAP)
        sims = argument.xpath(sim_xpath, namespaces=NS_MAP)
        for var in method_vars:
            text = var.text
            if text is None:
                text = get_flattern_text(var)
            result.append(text)
        for sim in sims:
            sim_name = get_method_call_name(sim)

            if '.' in sim_name:
                caller_name = sim_name.rsplit('.', 1)[:-1][0]
            else:
                caller_name = sim_name
            result.append(caller_name)
            # if not is_argument_none(sim):
            vars_in_sim = get_all_var_str_in_call(sim)
            for var in vars_in_sim:
                result.append(var)

    return result


def get_all_sim_str_in_call(method_xml):
    argument_xpath = './src:argument_list/src:argument'
    arguments = method_xml.xpath(argument_xpath, namespaces=NS_MAP)
    sim_xpath = './src:expr/src:call'

    result = []
    for index in range(0, len(arguments)):
        argument = arguments[index]
        sims = argument.xpath(sim_xpath, namespaces=NS_MAP)

        for sim in sims:
            sim_name = get_method_call_name(sim)
            result.append(sim_name)
            sims_in_sim = get_all_sim_str_in_call(sim)
            for method in sims_in_sim:
                result.append(method)

    return result


def get_verbosity_type(caller: str, verbosity: str):
    if caller == 'System.err':
        return LogVerbosityType.ERROR
    if caller == 'System.out':
        return LogVerbosityType.INFO

    verbosity_type = None
    if verbosity is not None:
        lowercase_verbosity = verbosity.lower()
        if lowercase_verbosity in ['v', 'verbose', 'logv', 'logverbose', 'verboselog', 'log_v', 'trace']:
            verbosity_type = LogVerbosityType.TRACE
        elif lowercase_verbosity in ['d', 'debug', 'fine', 'logd', 'logdebug', 'debuglog', 'log_d']:
            verbosity_type = LogVerbosityType.DEBUG
        elif lowercase_verbosity in ['i', 'info', 'log', 'logi', 'logln', 'loginfo', 'infolog', 'log_i',
                                     'print', 'printf', 'println', 'printlog', 'logmessage', 'logcommon',
                                     'logAuditEvent', 'logDnsLookup']:
            verbosity_type = LogVerbosityType.INFO
        elif lowercase_verbosity in ['w', 'warn', 'warning', 'logw', 'logwarning', 'logwarn', 'warnlog',
                                     'warninglog', 'log_w']:
            verbosity_type = LogVerbosityType.WARN
        elif lowercase_verbosity in ['e', 'error', 'severe', 'fatal', 'wtf', 'loge', 'logerror', 'logsevere',
                                     'logfatal',
                                     'logwtf', 'logexception', 'errlog', 'errorlog', 'severelog', 'fatallog', 'log_e']:
            verbosity_type = LogVerbosityType.ERROR

    return verbosity_type


def get_log_verbosity_num(xml_log_call_list):
    log_verbosity_list = []
    for xml_log_call in xml_log_call_list:
        log_call_name = get_method_call_name(xml_log_call)
        if '.' in log_call_name:
            caller_name = log_call_name.rsplit('.', 1)[:-1][0]
            level_name = log_call_name.rsplit('.', 1)[-1:][0]
        else:
            caller_name = log_call_name
            level_name = None

        log_verbosity = get_verbosity_type(caller_name, level_name)
        log_verbosity_list.append(log_verbosity)

    trace_num = log_verbosity_list.count(LogVerbosityType.TRACE)
    debug_num = log_verbosity_list.count(LogVerbosityType.DEBUG)
    info_num = log_verbosity_list.count(LogVerbosityType.INFO)
    warn_num = log_verbosity_list.count(LogVerbosityType.WARN)
    error_num = log_verbosity_list.count(LogVerbosityType.ERROR)

    return trace_num, debug_num, info_num, warn_num, error_num

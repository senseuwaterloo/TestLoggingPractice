import os
import re
import subprocess
from pathlib import Path
from lxml import etree

from models.log import LogArgumentType, LogCallerType, LogVerbosityType
from utils import file_util, shell_util

NS_MAP = {"src": "http://www.srcML.org/srcML/src"}


def get_logging_calls_xml_of_repo(repo_path: str):
    java_file_list = file_util.get_all_java_files(repo_path)
    total_result, total_assert_result, total_print_result, total_log_result = [], [], [], []
    test_result, test_assert_result, test_print_result, test_log_result = [], [], [], []
    production_result, production_assert_result, production_print_result, production_log_result = [], [], [], []

    total_trace, total_debug, total_info, total_warn, total_error = 0, 0, 0, 0, 0
    test_trace, test_debug, test_info, test_warn, test_error = 0, 0, 0, 0, 0
    production_trace, production_debug, production_info, production_warn, production_error = 0, 0, 0, 0, 0
    # total_result, test_result, production_result = [], [], []

    for java_file in java_file_list:
        total_calls, assert_calls, print_calls, log_calls, trace_num, debug_num, info_num, warn_num, error_num = get_logging_calls_xml_of_file(str(java_file))
        total_trace += trace_num
        total_debug += debug_num
        total_info += info_num
        total_warn += warn_num
        total_error += error_num
        total_result.extend(total_calls)
        total_assert_result.extend(assert_calls)
        total_print_result.extend(print_calls)
        total_log_result.extend(log_calls)
        if file_util.is_test_file(str(java_file)):
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

    trace_num, debug_num, info_num, warn_num, error_num = get_log_verbosity_num(total_result)

    return total_result, assert_result, print_result, log_result, trace_num, debug_num, info_num, warn_num, error_num


def get_methods_of_file(file_path: str):
    xml_name = file_util.generate_random_file_name_with_extension('xml')
    methods = []
    xml_p = None
    try:
        shell_util.run_command("srcml '{}' -o {}".format(file_path, xml_name))
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

    filter_caller_regex = '.*?(log|(system\.out)|(system\.err)|timber).*'
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


def get_logging_argument_type(method_xml) -> LogArgumentType:
    result = None
    arguments = get_logging_argument(method_xml)
    contains_text = False
    contains_var = False
    contains_sim = False
    for argument in arguments:
        if len(argument[0]) > 0:
            contains_text = True
        if len(argument[1]) > 0:
            contains_var = True
        if len(argument[2]) > 0:
            contains_sim = True

    if contains_text and not contains_var and not contains_sim:
        result = LogArgumentType.TEXT_ONLY
    elif contains_text and contains_var and not contains_sim:
        result = LogArgumentType.TEXT_VAR
    elif contains_text and not contains_var and contains_sim:
        result = LogArgumentType.TEXT_SIM
    elif contains_text and contains_var and contains_sim:
        result = LogArgumentType.TEXT_VAR_SIM
    elif contains_var and not contains_text and not contains_sim:
        result = LogArgumentType.VAR_ONLY
    elif contains_var and not contains_text and contains_sim:
        result = LogArgumentType.VAR_SIM
    elif contains_sim and not contains_text and not contains_var:
        # e.g. httpOperation.getUrl()
        result = LogArgumentType.SIM_ONLY

    return result


def get_logging_argument_number(method_xml):
    arguments = get_logging_argument(method_xml)
    var_num = 0
    text_length = 0

    if len(arguments) == 0:
        return var_num, text_length
    for argument in arguments:
        var_num = var_num + len(argument[1]) + len(argument[2])
        if len(argument[0]) > 0:
            for text_argument in argument[0]:
                log_text = transform_xml_str_to_code(etree.tostring(text_argument).decode('utf-8'))
                log_text = log_text.replace('"', '')
                log_text = log_text.replace('\\n', '')
                log_text = log_text.replace('\\t', '')
                text_length = text_length + len(log_text)
                # print(log_text)
                # print(text_length)

    # print(var_num)

    return var_num, text_length


def transform_xml_str_to_code(xml_str):
    pre_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><unit xmlns="http://www.srcML.org/srcML/src" revision="0.9.5" language="Java" filename="code_temp.java">'
    xml_str = pre_str + xml_str + '</unit>'
    fifo_name = file_util.generate_random_file_name_with_extension('xml')
    os.mkfifo(fifo_name)

    try:
        process = subprocess.Popen(['srcml', fifo_name], stdout=subprocess.PIPE)
        with open(fifo_name, 'w') as f:
            f.write(xml_str)
        output = process.stdout.read()
    finally:
        os.remove(fifo_name)
    return str(output)[2:-1]


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

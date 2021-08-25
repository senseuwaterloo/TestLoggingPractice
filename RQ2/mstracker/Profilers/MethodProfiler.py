import Levenshtein
from lxml import etree

from Models import Commit, Config
from Models.Log import LogChangeType, Log
from Profilers import XmlFileProfiler, DiffProfiler, LogProfiler


def compare_all_methods(methods_parent, methods_head, file_diff, head_commit_db: Commit):
    # file_added_logging_loc = 0
    # file_deleted_logging_loc = 0
    # file_updated_logging_loc = 0

    file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc = 0, 0, 0
    file_added_log_loc, file_deleted_log_loc, file_updated_log_loc = 0, 0, 0
    file_added_print_loc, file_deleted_print_loc, file_updated_print_loc = 0, 0, 0
    file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc = 0, 0, 0

    # get the string format so as to compare them
    method_parent_strings = [etree.tostring(method) for method in methods_parent]
    method_head_strings = [etree.tostring(method) for method in methods_head]

    # Get methods in parent and not in head
    methods_only_in_parent = get_complement_of_a_in_b(method_head_strings, method_parent_strings)
    # equals to [b'<root>' + method_str + b'</root>' for method_str in methods_only_in_parent]
    methods_only_in_parent = list(map((lambda method_str: b'<root>' + method_str + b'</root>'), methods_only_in_parent))

    # Get methods in head and not in parent. The rest methods are totally the same, so no change.
    methods_only_in_head = get_complement_of_a_in_b(method_parent_strings, method_head_strings)
    methods_only_in_head = list(map((lambda method_str: b'<root>' + method_str + b'</root>'), methods_only_in_head))

    methods_str_already_checked_in_parent = []
    methods_str_already_checked_in_head = []

    # 1. Compare methods with same signature.
    for method_parent_str in methods_only_in_parent:
        # method_parent_str = b'<root>' + method_parent_str + b'</root>'
        method_parent_xml = etree.fromstring(method_parent_str,
                                             etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
        for method_head_str in methods_only_in_head:
            # method_head_str = b'<root>' + method_head_str + b'</root>'
            if method_head_str in methods_str_already_checked_in_head:
                continue
            method_head_xml = etree.fromstring(method_head_str,
                                               etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            is_same_name, is_same_parameters = XmlFileProfiler.compare_method_signature(method_parent_xml,
                                                                                        method_head_xml)
            if is_same_name and is_same_parameters:
                # Methods with same signature, it is modified
                monitoring_method_calls_in_parent, assert_method_calls_in_parent, print_method_calls_in_parent, \
                    log_method_calls_in_parent = XmlFileProfiler.get_logging_calls_xml_of_method(method_parent_xml)

                monitoring_method_calls_in_head, assert_method_calls_in_head, print_method_calls_in_head, \
                    log_method_calls_in_head = XmlFileProfiler.get_logging_calls_xml_of_method(method_head_xml)

                method_name = XmlFileProfiler.get_method_full_signature(method_head_xml)
                method_added_monitoring_loc, method_deleted_monitoring_loc, method_updated_monitoring_loc, \
                    method_added_assert_loc, method_deleted_assert_loc, method_updated_assert_loc, \
                    method_added_print_loc, method_deleted_print_loc, method_updated_print_loc, \
                    method_added_log_loc, method_deleted_log_loc, method_updated_log_loc = \
                    compare_logging_method_calls(head_commit_db, file_diff, method_name, assert_method_calls_in_parent,
                                                 assert_method_calls_in_head, print_method_calls_in_parent,
                                                 print_method_calls_in_head, log_method_calls_in_parent,
                                                 log_method_calls_in_head)

                file_added_monitoring_loc += method_added_monitoring_loc
                file_deleted_monitoring_loc += method_deleted_monitoring_loc
                file_updated_monitoring_loc += method_updated_monitoring_loc
                file_added_log_loc += method_added_log_loc
                file_deleted_log_loc += method_deleted_log_loc
                file_updated_log_loc += method_updated_log_loc
                file_added_print_loc += method_added_print_loc
                file_deleted_print_loc += method_deleted_print_loc
                file_updated_print_loc += method_updated_print_loc
                file_added_assert_loc += method_added_assert_loc
                file_deleted_assert_loc += method_deleted_assert_loc
                file_updated_assert_loc += method_updated_assert_loc

                # file_added_logging_loc += method_added_logging_loc
                # file_deleted_logging_loc += method_deleted_logging_loc
                # file_updated_logging_loc += method_updated_logging_loc
                methods_str_already_checked_in_parent.append(method_parent_str)
                methods_str_already_checked_in_head.append(method_head_str)
                break

    # 2. Compare rest methods with different signature
    for method_parent_str in methods_only_in_parent:
        # method_parent_str = b'<root>' + method_parent_str + b'</root>'
        if method_parent_str in methods_str_already_checked_in_parent:
            continue
        method_parent_xml = etree.fromstring(method_parent_str,
                                             etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
        for method_head_str in methods_only_in_head:
            # method_head_str = b'<root>' + method_head_str + b'</root>'
            if method_head_str in methods_str_already_checked_in_head:
                continue
            method_head_xml = etree.fromstring(method_head_str,
                                               etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            is_same_name, is_same_parameters = XmlFileProfiler.compare_method_signature(method_parent_xml,
                                                                                        method_head_xml)
            block_content_str_in_parent = etree.tostring(XmlFileProfiler.get_method_block_content(method_parent_xml))
            block_content_str_in_head = etree.tostring(XmlFileProfiler.get_method_block_content(method_head_xml))
            if is_same_name and not is_same_parameters:
                #  if method name are same, that is parameter declaration change.
                if block_content_str_in_parent == block_content_str_in_head:
                    # text are same, no need to compare
                    pass
                else:
                    # if text not same, method is modified, deal with the same process above.
                    monitoring_method_calls_in_parent, assert_method_calls_in_parent, print_method_calls_in_parent, \
                        log_method_calls_in_parent = XmlFileProfiler.get_logging_calls_xml_of_method(method_parent_xml)
                    monitoring_method_calls_in_head, assert_method_calls_in_head, print_method_calls_in_head, \
                        log_method_calls_in_head = XmlFileProfiler.get_logging_calls_xml_of_method(method_head_xml)
                    method_name = XmlFileProfiler.get_method_full_signature(method_head_xml)
                    method_added_monitoring_loc, method_deleted_monitoring_loc, method_updated_monitoring_loc, \
                        method_added_assert_loc, method_deleted_assert_loc, method_updated_assert_loc, \
                        method_added_print_loc, method_deleted_print_loc, method_updated_print_loc, \
                        method_added_log_loc, method_deleted_log_loc, method_updated_log_loc \
                        = compare_logging_method_calls(head_commit_db, file_diff, method_name,
                                                       assert_method_calls_in_parent, assert_method_calls_in_head,
                                                       print_method_calls_in_parent, print_method_calls_in_head,
                                                       log_method_calls_in_parent, log_method_calls_in_head)
                    # file_added_logging_loc += method_added_logging_loc
                    # file_deleted_logging_loc += method_deleted_logging_loc
                    # file_updated_logging_loc += method_updated_logging_loc
                    file_added_monitoring_loc += method_added_monitoring_loc
                    file_deleted_monitoring_loc += method_deleted_monitoring_loc
                    file_updated_monitoring_loc += method_updated_monitoring_loc
                    file_added_log_loc += method_added_log_loc
                    file_deleted_log_loc += method_deleted_log_loc
                    file_updated_log_loc += method_updated_log_loc
                    file_added_print_loc += method_added_print_loc
                    file_deleted_print_loc += method_deleted_print_loc
                    file_updated_print_loc += method_updated_print_loc
                    file_added_assert_loc += method_added_assert_loc
                    file_deleted_assert_loc += method_deleted_assert_loc
                    file_updated_assert_loc += method_updated_assert_loc
                methods_str_already_checked_in_parent.append(method_parent_str)
                methods_str_already_checked_in_head.append(method_head_str)
            elif not is_same_name and not is_same_parameters:
                if block_content_str_in_parent == block_content_str_in_head:
                    # if text are same, no log changed. They are renamed method.
                    methods_str_already_checked_in_parent.append(method_parent_str)
                    methods_str_already_checked_in_head.append(method_head_str)

    # 3. For the rest methods, they are added or deleted
    for method_parent_str in methods_only_in_parent:
        # method_parent_str = b'<root>' + method_parent_str + b'</root>'
        if method_parent_str not in methods_str_already_checked_in_parent:
            # they are deleted, mark log calls in those methods as deleted.
            total_num, assert_num, print_num, log_num = DiffProfiler.save_logs_of_method_xml_str_if_needed(
                LogChangeType.DELETED_WITH_METHOD, file_diff.a_path, head_commit_db, method_parent_str)
            file_deleted_monitoring_loc += total_num
            file_deleted_log_loc += log_num
            file_deleted_print_loc += print_num
            file_deleted_assert_loc += assert_num

            # file_deleted_logging_loc += DiffProfiler.save_logs_of_method_xml_str_if_needed(
            #     LogChangeType.DELETED_WITH_METHOD,
            #     file_diff.a_path, head_commit_db,
            #     method_parent_str)
    for method_head_str in methods_only_in_head:
        # method_head_str = b'<root>' + method_head_str + b'</root>'
        if method_head_str not in methods_str_already_checked_in_head:
            # they are added, mark log calls in those methods as added.
            total_num, assert_num, print_num, log_num = DiffProfiler.save_logs_of_method_xml_str_if_needed(
                LogChangeType.ADDED_WITH_METHOD, file_diff.b_path, head_commit_db, method_head_str)
            file_added_monitoring_loc += total_num
            file_added_log_loc += log_num
            file_added_print_loc += print_num
            file_added_assert_loc += assert_num

            # file_added_logging_loc += DiffProfiler.save_logs_of_method_xml_str_if_needed(
            #     LogChangeType.ADDED_WITH_METHOD,
            #     file_diff.b_path, head_commit_db,
            #     method_head_str)

    return file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc, \
        file_added_log_loc, file_deleted_log_loc, file_updated_log_loc, \
        file_added_print_loc, file_deleted_print_loc, file_updated_print_loc, \
        file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc


def get_complement_of_a_in_b(a_collection, b_collection):
    return [x for x in b_collection if x not in a_collection]
    # result = []
    # for item in b_collection:
    #     if item not in a_collection:
    #         result.append(item)
    # return result


def compare_logging_method_calls(head_commit_db: Commit, file_diff, method_name, assert_method_calls_parent,
                                 assert_method_calls_head, print_method_calls_parent, print_method_calls_head,
                                 log_method_calls_parent, log_method_calls_head):
    # method_mapping_list = []
    method_assert_mapping_list, method_print_mapping_list, method_log_mapping_list = [], [], []

    method_added_monitoring_loc, method_deleted_monitoring_loc, method_updated_monitoring_loc = 0, 0, 0
    method_added_assert_loc, method_deleted_assert_loc, method_updated_assert_loc = 0, 0, 0
    method_added_print_loc, method_deleted_print_loc, method_updated_print_loc = 0, 0, 0
    method_added_log_loc, method_deleted_log_loc, method_updated_log_loc = 0, 0, 0

    method_assert_mapping_list, assert_calls_str_parent, assert_calls_str_head \
        = populate_and_get_mapping_list(assert_method_calls_parent, assert_method_calls_head,
                                        method_assert_mapping_list)
    method_print_mapping_list, print_calls_str_parent, print_calls_str_head\
        = populate_and_get_mapping_list(print_method_calls_parent, print_method_calls_head, method_print_mapping_list)
    method_log_mapping_list, log_calls_str_parent, log_calls_str_head\
        = populate_and_get_mapping_list(log_method_calls_parent, log_method_calls_head, method_log_mapping_list)
    method_assert_calls_mapping_in_parent = [mapping[0] for mapping in method_assert_mapping_list]
    method_assert_calls_mapping_in_head = [mapping[1] for mapping in method_assert_mapping_list]
    method_print_calls_mapping_in_parent = [mapping[0] for mapping in method_print_mapping_list]
    method_print_calls_mapping_in_head = [mapping[1] for mapping in method_print_mapping_list]
    method_log_calls_mapping_in_parent = [mapping[0] for mapping in method_log_mapping_list]
    method_log_calls_mapping_in_head = [mapping[1] for mapping in method_log_mapping_list]

    deleted_assert_calls_str = list(set(assert_calls_str_parent) - set(method_assert_calls_mapping_in_parent))
    added_assert_calls_str = list(set(assert_calls_str_head) - set(method_assert_calls_mapping_in_head))

    deleted_print_calls_str = list(set(print_calls_str_parent) - set(method_print_calls_mapping_in_parent))
    added_print_calls_str = list(set(print_calls_str_head) - set(method_print_calls_mapping_in_head))

    deleted_log_calls_str = list(set(log_calls_str_parent) - set(method_log_calls_mapping_in_parent))
    added_log_calls_str = list(set(log_calls_str_head) - set(method_log_calls_mapping_in_head))

    method_deleted_assert_loc += len(deleted_assert_calls_str)
    method_added_assert_loc += len(added_assert_calls_str)
    method_deleted_print_loc += len(deleted_print_calls_str)
    method_added_print_loc += len(added_print_calls_str)
    method_deleted_log_loc += len(deleted_log_calls_str)
    method_added_log_loc += len(added_log_calls_str)

    if not head_commit_db.is_merge_commit:
        for call_str in deleted_assert_calls_str + deleted_print_calls_str + deleted_log_calls_str:
            call_xml = etree.fromstring(_get_code_xml_str_from_compare(call_str),
                                        etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            DiffProfiler.save_logs_of_logging_call_xml(call_xml, LogChangeType.DELETED_INSIDE_METHOD, file_diff.a_path,
                                                       head_commit_db, method_name)

        for call_str in added_assert_calls_str + added_print_calls_str + added_log_calls_str:
            call_xml = etree.fromstring(_get_code_xml_str_from_compare(call_str),
                                        etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            DiffProfiler.save_logs_of_logging_call_xml(call_xml, LogChangeType.ADDED_INSIDE_METHOD, file_diff.b_path,
                                                       head_commit_db, method_name)

        method_updated_assert_loc = detect_and_save_updated_calls(method_assert_mapping_list, method_updated_assert_loc,
                                                                  head_commit_db, file_diff, method_name)
        method_updated_print_loc = detect_and_save_updated_calls(method_print_mapping_list, method_updated_print_loc,
                                                                 head_commit_db, file_diff, method_name)
        method_updated_log_loc = detect_and_save_updated_calls(method_log_mapping_list, method_updated_log_loc,
                                                               head_commit_db, file_diff, method_name)

        method_added_monitoring_loc = method_added_assert_loc + method_added_print_loc + method_added_log_loc
        method_deleted_monitoring_loc = method_deleted_assert_loc + method_deleted_print_loc + method_deleted_log_loc
        method_updated_monitoring_loc = method_updated_assert_loc + method_updated_print_loc + method_updated_log_loc

    # Add index to make each call unique.
    # method_calls_str_parent = \
    #     [str(index) + '#' + etree.tostring(call).decode('utf-8') for index, call in
    #      enumerate(monitoring_method_calls_parent)]
    # method_calls_str_head = \
    #     [str(index) + '#' + etree.tostring(call).decode('utf-8') for index, call in
    #      enumerate(monitoring_method_calls_head)]
    # compare the logging call in parent to the logging call in head one by one and find the most matched one
    # for call_str_in_parent in method_calls_str_parent:
    #     for call_str_in_head in method_calls_str_head:
    #         distance_ratio = Levenshtein.ratio(XmlFileProfiler.transform_xml_str_to_code(call_str_in_parent),
    #                                            XmlFileProfiler.transform_xml_str_to_code(call_str_in_head))
    #         if distance_ratio > Config.LEVENSHTEIN_RATIO_THRESHOLD:
    #             is_parent_in_mapping = False
    #             # Check mapping list
    #             for mapping in method_mapping_list:
    #                 call_mapping_parent = mapping[0]
    #                 mapping_ratio = mapping[2]
    #                 if call_str_in_parent == call_mapping_parent:
    #                     is_parent_in_mapping = True
    #                     # the bigger the more similar
    #                     if distance_ratio > mapping_ratio:
    #                         mapping[1] = call_str_in_head
    #                         mapping[2] = Levenshtein.ratio(_get_code_text_from_compare(call_str_in_parent),
    #                                                        _get_code_text_from_compare(call_str_in_head))
    #             if not is_parent_in_mapping:
    #                 is_head_in_mapping = False
    #                 for mapping in method_mapping_list:
    #                     call_mapping_head = mapping[1]
    #                     mapping_ratio = mapping[2]
    #                     if call_str_in_head == call_mapping_head:
    #                         is_head_in_mapping = True
    #                         if distance_ratio > mapping_ratio:
    #                             mapping[0] = call_str_in_parent
    #                             mapping[2] = Levenshtein.ratio(_get_code_text_from_compare(call_str_in_parent),
    #                                                            _get_code_text_from_compare(call_str_in_head))
    #                 if not is_head_in_mapping:
    #                     method_mapping_list.append([call_str_in_parent, call_str_in_head, distance_ratio])

    # method_calls_mapping_in_parent = [mapping[0] for mapping in method_mapping_list]
    # method_calls_mapping_in_head = [mapping[1] for mapping in method_mapping_list]
    #
    # deleted_logging_calls_str = list(set(method_calls_str_parent) - set(method_calls_mapping_in_parent))
    # added_logging_calls_str = list(set(method_calls_str_head) - set(method_calls_mapping_in_head))
    #
    # method_deleted_monitoring_loc += len(deleted_logging_calls_str)
    # method_added_monitoring_loc += len(added_logging_calls_str)

    # if not head_commit_db.is_merge_commit:
    #     for call_str in deleted_logging_calls_str:
    #         call_xml = etree.fromstring(_get_code_xml_str_from_compare(call_str),
    #         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    #         DiffProfiler.save_logs_of_logging_call_xml(call_xml, LogChangeType.DELETED_INSIDE_METHOD,
    #         file_diff.a_path, head_commit_db, method_name)
    #
    #     for call_str in added_logging_calls_str:
    #         call_xml = etree.fromstring(_get_code_xml_str_from_compare(call_str),
    #         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    #         DiffProfiler.save_logs_of_logging_call_xml(call_xml, LogChangeType.ADDED_INSIDE_METHOD, file_diff.b_path,
    #                                                    head_commit_db, method_name)

    # for mapping in method_mapping_list:
    #     change_from = _get_code_text_from_compare(mapping[0])
    #     change_to = _get_code_text_from_compare(mapping[1])
    #     if change_from != change_to:
    #         # True Update
    #         logging_method_parent_xml = etree.fromstring(_get_code_xml_str_from_compare(mapping[0]),
    #         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    #         logging_method_head_xml = etree.fromstring(_get_code_xml_str_from_compare(mapping[1]),
    #         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    #         update_type = None
    #         method_updated_monitoring_loc += 1
    #         if not head_commit_db.is_merge_commit:
    #             call_name = XmlFileProfiler.get_method_call_name(logging_method_head_xml)
    #             if '.' in call_name:
    #                 verbosity = call_name.split('.')[-1]
    #             else:
    #                 verbosity = call_name
    #             _, verbosity_type = LogProfiler.get_log_content_component(change_to)
    #             argument_type = LogProfiler.get_logging_argument_type(logging_method_head_xml)
    #             log = Log.create(commit=head_commit_db, file_path=file_diff.b_path, embed_method=method_name,
    #                       change_type=LogChangeType.UPDATED, content=change_to, content_update_from=change_from,
    #                       verbosity=verbosity, verbosity_type=verbosity_type, argument_type=argument_type,
    #                       update_type=update_type)
    #             log.update_type = LogProfiler.get_log_update_detail(log)
    #             log.is_consistent_update = LogProfiler.is_log_consistent_update(log)
    #             log.is_test_log = LogProfiler.is_test_log(log)
    #             log.save()

    return method_added_monitoring_loc, method_deleted_monitoring_loc, method_updated_monitoring_loc, \
        method_added_assert_loc, method_deleted_assert_loc, method_updated_assert_loc, \
        method_added_print_loc, method_deleted_print_loc, method_updated_print_loc, \
        method_added_log_loc, method_deleted_log_loc, method_updated_log_loc


def _get_code_xml_str_from_compare(xml_str):
    return xml_str.split('#', 1)[1]


def _get_code_text_from_compare(xml_str):
    return XmlFileProfiler.transform_xml_str_to_code(_get_code_xml_str_from_compare(xml_str))


def populate_and_get_mapping_list(logging_method_calls_parent, logging_method_calls_head, method_mapping_list):
    # Add index to make each call unique.
    method_calls_str_parent = \
        [str(index) + '#' + etree.tostring(call).decode('utf-8') for index, call in
         enumerate(logging_method_calls_parent)]
    method_calls_str_head = \
        [str(index) + '#' + etree.tostring(call).decode('utf-8') for index, call in
         enumerate(logging_method_calls_head)]
    # compare the logging call in parent to the logging call in head one by one and find the most matched one
    for call_str_in_parent in method_calls_str_parent:
        for call_str_in_head in method_calls_str_head:
            distance_ratio = Levenshtein.ratio(XmlFileProfiler.transform_xml_str_to_code(call_str_in_parent),
                                               XmlFileProfiler.transform_xml_str_to_code(call_str_in_head))
            if distance_ratio > Config.LEVENSHTEIN_RATIO_THRESHOLD:
                is_parent_in_mapping = False
                # Check mapping list
                for mapping in method_mapping_list:
                    call_mapping_parent = mapping[0]
                    mapping_ratio = mapping[2]
                    if call_str_in_parent == call_mapping_parent:
                        is_parent_in_mapping = True
                        # the bigger the more similar
                        if distance_ratio > mapping_ratio:
                            mapping[1] = call_str_in_head
                            mapping[2] = Levenshtein.ratio(_get_code_text_from_compare(call_str_in_parent),
                                                           _get_code_text_from_compare(call_str_in_head))
                if not is_parent_in_mapping:
                    is_head_in_mapping = False
                    for mapping in method_mapping_list:
                        call_mapping_head = mapping[1]
                        mapping_ratio = mapping[2]
                        if call_str_in_head == call_mapping_head:
                            is_head_in_mapping = True
                            if distance_ratio > mapping_ratio:
                                mapping[0] = call_str_in_parent
                                mapping[2] = Levenshtein.ratio(_get_code_text_from_compare(call_str_in_parent),
                                                               _get_code_text_from_compare(call_str_in_head))
                    if not is_head_in_mapping:
                        method_mapping_list.append([call_str_in_parent, call_str_in_head, distance_ratio])

    return method_mapping_list, method_calls_str_parent, method_calls_str_head


def detect_and_save_updated_calls(method_mapping_list, method_updated_monitoring_loc, head_commit_db,
                                  file_diff, method_name):
    for mapping in method_mapping_list:
        change_from = _get_code_text_from_compare(mapping[0])
        change_to = _get_code_text_from_compare(mapping[1])
        if change_from != change_to:
            # True Update
            logging_method_parent_xml = etree.fromstring(_get_code_xml_str_from_compare(mapping[0]),
                                                         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            logging_method_head_xml = etree.fromstring(_get_code_xml_str_from_compare(mapping[1]),
                                                       etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            update_type = None
            method_updated_monitoring_loc += 1
            if not head_commit_db.is_merge_commit:
                call_name = XmlFileProfiler.get_method_call_name(logging_method_head_xml)
                call_type = XmlFileProfiler.get_log_call_type(logging_method_head_xml)
                if '.' in call_name:
                    verbosity = call_name.split('.')[-1]
                else:
                    verbosity = call_name
                _, verbosity_type = LogProfiler.get_log_content_component(change_to)
                argument_type = LogProfiler.get_logging_argument_type(logging_method_head_xml)
                log = Log.create(commit=head_commit_db, file_path=file_diff.b_path, embed_method=method_name,
                                 change_type=LogChangeType.UPDATED, content=change_to, content_update_from=change_from,
                                 verbosity=verbosity, verbosity_type=verbosity_type, argument_type=argument_type,
                                 call_type=call_type)
                log.update_type = LogProfiler.get_log_update_detail(log)
                log.is_consistent_update = LogProfiler.is_log_consistent_update(log)
                log.is_test_log = LogProfiler.is_test_log(log)
                log.save()

    return method_updated_monitoring_loc


# def is_log_consistent_update(log: Log):
#     """ THIS METHOD SHOULD BE CALLED AFTER LOG UPDATE_TYPE IS DETERMINED """
#     if log.update_type is None:
#         return None
#
#     if not (LogUpdateType.ADDED_VAR in log.update_type or
#             LogUpdateType.DELETED_VAR in log.update_type or
#             LogUpdateType.REPLACED_VAR in log.update_type):
#         return False
#
#     commit = log.commit
#     repo = commit.repo
#     repo_path = Config.get_repo_local_path_with_project_name(repo.project_name)
#     commit_id = commit.commit_id
#     parent_commit_id = commit.parent_commit_id
#     file_path = log.file_path
#     output = BashUtil.run(r"git diff -U0 {} {} -- '{}' | grep '^[+]' | grep -Ev '^(--- a/|\+\+\+ b/)'".format
#                              (parent_commit_id, commit_id, file_path), cwd=repo_path)
#     lines = output.splitlines()
#     log_xml_obj = XmlFileProfiler.transform_log_str_to_xml_obj(log.content)
#     all_vars_in_log = XmlFileProfiler.get_all_var_str_in_call(log_xml_obj)
#     all_vars_set = set(all_vars_in_log)
#     is_consistent_update = False
#     for line in lines:
#         line = line[1:].strip()
#         if line in log.content:
#             break
#         if line.startswith('//') or line.startswith('/*'):
#             continue
#         if line.endswith(';') and '=' in line:
#             possible_var_statement = line.split('=')[0]
#             if len(possible_var_statement) > 0 and '"' not in possible_var_statement:
#                 # '=' is not in a string or comment
#                 possible_var = possible_var_statement.split()[-1]
#                 if possible_var in all_vars_set:
#                     is_consistent_update = True
#                     break
#         elif line.endswith('{'):
#             possible_var_statement = line.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
#             if len(all_vars_set.intersection(set(possible_var_statement))) > 0:
#                 is_consistent_update = True
#                 break
#
#     return is_consistent_update


# def is_test_log(log: Log):
#     file_path = log.file_path
#     return FileUtil.is_test_file(file_path)

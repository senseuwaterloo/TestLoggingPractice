from Models import Config
from Models.Log import LogArgumentType, Log, LogChangeType, LogUpdateType
from Profilers import XmlFileProfiler
from Profilers.XmlFileProfiler import get_verbosity_type
from Utils import FileUtil, BashUtil


def get_log_content_component(content: str):
    caller_method = content.split('(')[0]
    caller_method = ''.join(caller_method.split())
    if '.' in caller_method:
        verbosity = caller_method.split('.')[-1]
        caller_object = caller_method.rsplit('.', 1)[0]
    else:
        caller_object = caller_method
        verbosity = caller_method
    verbosity_type = get_verbosity_type(caller_object, verbosity)
    arguments_str = content[len(caller_method) + 1: -1]
    # arguments = arguments_str.split(',')
    return caller_object, verbosity_type


def get_logging_argument_type(method_xml) -> LogArgumentType:
    result = None
    arguments = XmlFileProfiler.get_logging_argument(method_xml)
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


def get_log_update_detail(log: Log):
    if log.change_type != LogChangeType.UPDATED:
        return None

    update_type = ''
    old_content = log.content_update_from.replace('\\n', '').replace('\\t', '').replace('\\r', '')
    new_content = log.content.replace('\\n', '').replace('\\t', '').replace('\\r', '')
    if ''.join(old_content.split()) == ''.join(new_content.split()):
        update_type = LogUpdateType.UPDATED_FORMAT
    else:
        # Check logging method and verbosity
        old_caller_object, old_verbosity_type = get_log_content_component(old_content)
        new_caller_object, new_verbosity_type = get_log_content_component(new_content)
        if old_caller_object != new_caller_object:
            update_type = LogUpdateType.UPDATED_LOGGING_METHOD
        if old_verbosity_type is not None \
                and new_verbosity_type is not None \
                and old_verbosity_type != new_verbosity_type:
            update_type = update_type + '+' + LogUpdateType.UPDATED_VERBOSITY + '_' + old_verbosity_type + '_TO_' + new_verbosity_type

        # Check argument
        new_log_xml = XmlFileProfiler.transform_log_str_to_xml_obj(new_content)
        new_log_texts = XmlFileProfiler.get_all_text_str_in_call(new_log_xml)
        new_log_vars = XmlFileProfiler.get_all_var_str_in_call(new_log_xml)
        new_log_sims = XmlFileProfiler.get_all_sim_str_in_call(new_log_xml)

        old_log_xml = XmlFileProfiler.transform_log_str_to_xml_obj(old_content)
        old_log_texts = XmlFileProfiler.get_all_text_str_in_call(old_log_xml)
        old_log_vars = XmlFileProfiler.get_all_var_str_in_call(old_log_xml)
        old_log_sims = XmlFileProfiler.get_all_sim_str_in_call(old_log_xml)

        if new_log_xml is not None and old_log_xml is not None:
            # Check text
            if len(new_log_texts) > len(old_log_texts):
                update_type = update_type + '+' + LogUpdateType.ADDED_TEXT
            elif len(new_log_texts) < len(old_log_texts):
                update_type = update_type + '+' + LogUpdateType.DELETED_TEXT
            else:
                new_words = sum([x.split() for x in new_log_texts], [])
                old_words = sum([x.split() for x in old_log_texts], [])
                if len(new_words) > len(old_words):
                    update_type = update_type + '+' + LogUpdateType.ADDED_TEXT
                elif len(new_words) < len(old_words):
                    update_type = update_type + '+' + LogUpdateType.DELETED_TEXT
                else:
                    new_text_set = set(new_log_texts) - set(old_log_texts)
                    if len(new_text_set) > 0:
                        update_type = update_type + '+' + LogUpdateType.REPLACED_TEXT

            # Check var
            if len(new_log_vars) > len(old_log_vars):
                update_type = update_type + '+' + LogUpdateType.ADDED_VAR
            if len(new_log_vars) < len(old_log_vars):
                update_type = update_type + '+' + LogUpdateType.DELETED_VAR
            else:
                new_var_set = set(new_log_vars) - set(old_log_vars)
                if len(new_var_set) > 0:
                    update_type = update_type + '+' + LogUpdateType.REPLACED_VAR

            # Check SIM
            if len(new_log_sims) > len(old_log_sims):
                update_type = update_type + '+' + LogUpdateType.ADDED_SIM
            if len(new_log_sims) < len(old_log_sims):
                update_type = update_type + '+' + LogUpdateType.DELETED_SIM
            else:
                new_log_set = set(new_log_sims) - set(old_log_sims)
                if len(new_log_set) > 0:
                    update_type = update_type + '+' + LogUpdateType.REPLACED_SIM

    if update_type.startswith('+'):
        update_type = update_type[1:]

    if update_type == '':
        return None
    else:
        return update_type


def is_test_log(log: Log):
    file_path = log.file_path
    return FileUtil.is_test_file(file_path)


def is_log_consistent_update(log: Log):
    """ THIS METHOD SHOULD BE CALLED AFTER LOG UPDATE_TYPE IS DETERMINED """
    if log.update_type is None:
        return None

    if not (LogUpdateType.ADDED_VAR in log.update_type or
            LogUpdateType.DELETED_VAR in log.update_type or
            LogUpdateType.REPLACED_VAR in log.update_type):
        return False

    commit = log.commit
    repo = commit.repo
    repo_path = Config.get_repo_local_path_with_project_name(repo.project_name)
    commit_id = commit.commit_id
    parent_commit_id = commit.parent_commit_id
    file_path = log.file_path
    output = BashUtil.run(r"git diff -U0 {} {} -- '{}' | grep '^[+]' | grep -Ev '^(--- a/|\+\+\+ b/)'".format
                          (parent_commit_id, commit_id, file_path), cwd=repo_path)
    lines = output.splitlines()
    log_xml_obj = XmlFileProfiler.transform_log_str_to_xml_obj(log.content)
    all_vars_in_log = XmlFileProfiler.get_all_var_str_in_call(log_xml_obj)
    all_vars_set = set(all_vars_in_log)
    is_consistent_update = False
    for line in lines:
        line = line[1:].strip()
        if line in log.content:
            break
        if line.startswith('//') or line.startswith('/*'):
            continue
        if line.endswith(';') and '=' in line:
            possible_var_statement = line.split('=')[0]
            if len(possible_var_statement) > 0 and '"' not in possible_var_statement:
                # '=' is not in a string or comment
                possible_var = possible_var_statement.split()[-1]
                if possible_var in all_vars_set:
                    is_consistent_update = True
                    break
        elif line.endswith('{'):
            possible_var_statement = line.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            if len(all_vars_set.intersection(set(possible_var_statement))) > 0:
                is_consistent_update = True
                break

    return is_consistent_update

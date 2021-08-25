class Loc(object):
    files_num = 0
    blank_num = 0
    comment_num = 0
    code_num = 0

    def __init__(self, files_num=0, blank_num=0, comment_num=0, code_num=0):
        self.files_num = files_num
        self.blank_num = blank_num
        self.comment_num = comment_num
        self.code_num = code_num

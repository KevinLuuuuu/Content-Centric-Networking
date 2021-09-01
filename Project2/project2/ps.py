class PS():
    def __init__(self):
        self.ps = []

    def Creat_ps(self, route_ID, route_num, content_num, producer_content):
        for i in range(len(producer_content)):
            self.ps.append(producer_content[i])

    def Get_ps(self):
        return self.ps

    def Search_ps_interest(self, ps, content_name):
        for i in ps:
            if i == content_name:
                return True
        return False
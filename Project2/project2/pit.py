class PIT():
    def __init__(self):
        self.pit = {}

    def Get_pit(self):
        return self.pit

    def Get_pit_entry(self, content_name):
        return self.pit[content_name]

    def Update_pit_outface(self, pit, Outfaces, interest):
        pit[interest['content_name']][1].append(Outfaces)

    def Merge_pit_entry(self, interest):
        duplicate = False
        for i in self.pit[interest['content_name']][0]:
            if i == interest['route_ID']:        #??
                duplicate = True
                break
        if not duplicate:
            self.pit[interest['content_name']][0].append(interest['route_ID'])      #??

    def Creat_pit_entry(self, interest):
        self.pit[interest['content_name']] = [[interest['route_ID']], []]        #??

    def Search_pit_interest(self, pit, interest):
        if interest['content_name'] in pit:
            return True
        return False

    def Search_pit_data(self, pit, data):
        if data['content_name'] in pit:
            return True

    def Remove_pit_entry(self, pit, data):
        del self.pit[data['content_name']]
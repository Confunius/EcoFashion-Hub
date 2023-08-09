class Admin:
    count_id = 0
    def __init__(self,adminFirstName,adminLastName,adminUserName,adminPassword,adminEmail, adminCfmPassword, adminPhoneNumber, adminVerified = 1): # initializer method    def __init__(self, userName, userPassword, userEmail, userCfmEmail):
        Admin.count_id += 1
        self.__admin_id = Admin.count_id
        self.__adminFirstName = adminFirstName
        self.__adminLastName = adminLastName
        self.__adminUserName = adminUserName
        self.__adminPassword = adminPassword
        self.__adminEmail = adminEmail
        self.__adminCfmPassword = adminCfmPassword
        self.__adminPhoneNumber = adminPhoneNumber
        self.__adminVerified = adminVerified

    def __repr__(self):
        return f'<User: {self.__adminUserName}>'    # accessor methods

    def get_admin_id(self):
        return self.__admin_id

    def get_adminFirstName(self):
        return self.__adminFirstName

    def get_adminLastName(self):
        return self.__adminLastName

    def get_adminUserName(self):
        return self.__adminUserName

    def get_adminPassword(self):
        return self.__adminPassword

    def get_adminEmail(self):
        return self.__adminEmail

    def get_adminCfmPassword(self):
        return self.__adminCfmPassword

    def get_adminPhoneNumber(self):
        return self.__adminPhoneNumber

    def get_adminVerified(self):
        return self.__adminVerified

    def set_admin_id(self, admin_id):
        self.__admin_id = admin_id

    def set_adminFirstName(self, adminFirstName):
        self.__adminFirstName = adminFirstName

    def set_adminLastName(self, adminLastName):
        self.__adminLastName = adminLastName

    def set_adminUserName(self, adminUserName):
        self.__adminUserName = adminUserName

    def set_adminPassword(self, adminPassword):
        self.__adminPassword = adminPassword

    def set_adminEmail(self, adminEmail):
        self.__adminEmail = adminEmail

    def set_adminCfmPassword(self, adminCfmPassword):
        self.__adminCfmPassword = adminCfmPassword

    def set_adminPhoneNumber(self, adminPhoneNumber):
        self.__adminPhoneNumber = adminPhoneNumber

    def set_adminVerified(self, adminVerified):
        self.__adminVerified = adminVerified

class TemplateReader:
    def __init__(self):
        pass

    def read_course_template(self,course_name):
        if course_name == 'CoronaFAQ':            
            try:
                email_file = open("email_templates/CoronaFAQ.html", "r")
                email_message = email_file.read()
                print('success')
                return email_message
            
                
                #if (course_name=='CoronaFAQ'):
                    #elif (course_name=='MachineLearningMasters'):
                 #   email_file = open("email_templates/MLM_Template.html", "r")
                   # email_message = email_file.read()
            except Exception as e:
                print('The exception is '+str(e))

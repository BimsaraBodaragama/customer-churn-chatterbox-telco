from pyexpat import features
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import joblib
import numpy as np

views = Blueprint('views', __name__)

model= joblib.load("random-forest")
# model = pickle.load(open("model.pkl", "rb"))
views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    src="{{iframe+&navContentPaneEnabled=false}}"
    # iframe = 'https://app.powerbi.com/view?r=eyJrIjoiMTljZWE0ZDItMzc0YS00YzY2LWI1YjEtNTFlZGU1YzBhYTUxIiwidCI6ImFhYzBjNTY0LTZjNWUtNGIwNS04ZGMzLTQwODA4N2Y3N2Y3NiIsImMiOjEwfQ%3D%3D&pageName=ReportSection'
    iframe = 'https://app.powerbi.com/view?r=eyJrIjoiMTljZWE0ZDItMzc0YS00YzY2LWI1YjEtNTFlZGU1YzBhYTUxIiwidCI6ImFhYzBjNTY0LTZjNWUtNGIwNS04ZGMzLTQwODA4N2Y3N2Y3NiIsImMiOjEwfQ%3D%3D&pageName=ReportSection'
    return render_template('home.html', iframe=iframe, user=current_user)


@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():

    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
    #return render_template("notes.html", user=current_user)


@views.route('/predict', methods=['GET', 'POST'])
@login_required
def Predict():
    output = ''
    return_features = []
    model_features = []
    voice_mail_plan_str = "Yes"
    churned = True
    
    def predict():
        # Put all form entries values in a list
        features = [float(i) for i in request.form.values()]
        for i in features:
            print(i)
            return_features.append(i)  
  
        acc_len_f = features[0]
        l_code_f = features[1]
        custom_calls_f = features[2]
        intl_plan_f = features[3]
        vm_plan_f = features[4]
        vm_msgs_f = features[5]
        tot_day_min_f = features[6]
        tot_day_call_f = features[7]
        tot_day_ch_f = features[8]
        tot_eve_min_f = features[9]
        tot_eve_call_f = features[10]
        tot_eve_ch_f = features[11]
        tot_nyt_min_f = features[12]
        tot_nyt_call_f = features[13]
        tot_nyt_ch_f = features[14]
        tot_intl_min_f = features[15] 
        tot_intl_call_f = features[16]
        tot_intl_ch_f = features[17]

        avg_day_call_f = division_for_model(tot_day_min_f, tot_day_call_f)
        avg_eve_call_f = division_for_model(tot_eve_min_f, tot_eve_call_f)
        avg_nyt_call_f = division_for_model(tot_nyt_min_f, tot_nyt_call_f)
        avg_intl_call_f = division_for_model(tot_intl_min_f, tot_intl_call_f)

        #INPUT PARAM ORDER
        #acclen, lcode, customcalls, intlplan, vmplan, vmmsgs, totdaymin, totdaycall, totdaych, totevemin, totevecal, totevech,
        #totnigmin, totnigcal, totnigch, totintlmin, totintlcal, totintlch 

        #MODEL NEEDED ORDER
        #['account_length', 'location_code', 'intertiol_plan', 'voice_mail_plan',
       #'number_vm_messages', 'total_day_charge', 'total_eve_charge',
       #'total_night_charge', 'total_intl_charge', 'customer_service_calls',
       #'avg_day_calls', 'avg_eve_calls', 'avg_night_calls',
       #'avg_intl_calls'] 

        model_features.append(acc_len_f)
        model_features.append(l_code_f)
        model_features.append(intl_plan_f)
        model_features.append(vm_plan_f)
        model_features.append(vm_msgs_f)
        model_features.append(tot_day_ch_f)
        model_features.append(tot_eve_ch_f)
        model_features.append(tot_nyt_ch_f)
        model_features.append(tot_intl_ch_f)
        model_features.append(custom_calls_f)
        model_features.append(avg_day_call_f)
        model_features.append(avg_eve_call_f)
        model_features.append(avg_nyt_call_f)
        model_features.append(avg_intl_call_f)

        m_f_i =0
        for m_f in model_features:
            print(m_f_i)
            print(m_f)
            m_f_i+=1
  

        # Convert features to array
        array_features = [np.array(model_features)]
        # Predict features
        prediction = model.predict(array_features)
        return prediction

    def get_intertiol_plan_str(return_features):
        if return_features[3]==0.0:
            intertiol_plan_str_temp = "No"
        else:    
            intertiol_plan_str_temp = "Yes"
        return intertiol_plan_str_temp  

    def get_voice_mail_plan_str(return_features):
        if return_features[4]==0.0:
            voice_mail_plan_str_temp = "No"
        else:    
            voice_mail_plan_str_temp = "Yes"
        return voice_mail_plan_str_temp         

    def division_for_model(num, den):
        if(den==0.0):
            return 0
        if(den==0):
            return 0
        return num/den

    def division(num, den):
        if(den==0.0):
            return "#N/A"
        if(den==0):
            return "#N/A" 
        return num/den     
        
    def floatOrNA(input):
        if(input=="#N/A"):
            return "#N/A" 
        output = round(input,2) 
        return output    

    if request.method == 'POST':
        output = predict()
        intertiol_plan_str = get_intertiol_plan_str(return_features) 
        voice_mail_plan_str = get_voice_mail_plan_str(return_features) 

        account_length_p= (int)(return_features[0])
        location_code_p= (int)(return_features[1])
        customer_service_calls_p= (int)(return_features[2])
        intertiol_plan_p= intertiol_plan_str
        voice_mail_plan_p= voice_mail_plan_str
        number_vm_messages_p= (int)(return_features[5])

        total_day_min_p= return_features[6]
        total_day_calls_p= (int)(return_features[7])
        total_day_charge_p= return_features[8]

        total_eve_min_p= return_features[9]
        total_eve_calls_p= (int)(return_features[10])
        total_eve_charge_p= return_features[11]
        
        total_night_minutes_p= return_features[12]
        total_night_calls_p= (int)(return_features[13])
        total_night_charge_p= return_features[14]

        total_intl_minutes_p= (float)(return_features[15])
        total_intl_calls_p= (int)(return_features[16])
        total_intl_charge_p= (float)(return_features[17])
        
        total_local_min_p= (float)(total_day_min_p) + (float)(total_eve_min_p) + (float)(total_night_minutes_p)
        total_local_calls_p= (int)(total_day_calls_p) + (int)(total_eve_calls_p) + (int)(total_night_calls_p)
        total_local_charge_p= (float)(total_day_charge_p) + (float)(total_eve_charge_p) + (float)(total_night_charge_p)
        
        total_min_p= (float)(total_local_min_p) + (float)(total_intl_minutes_p)
        total_calls_p= (int)(total_local_calls_p) + (int)(total_intl_calls_p)
        total_charge_p= (float)(total_local_charge_p) + (float)(total_intl_charge_p)

        avg_lcl_cls_p = division(total_local_min_p,total_local_calls_p)
        avg_intl_cls_p = division(total_intl_minutes_p,total_intl_calls_p)
        avg_tot_cls_p = division(total_min_p,total_calls_p)
        
        avg_local_calls_p= str(floatOrNA(avg_lcl_cls_p))
        avg_intl_calls_p= str(floatOrNA(avg_intl_cls_p))
        avg_total_calls_p= str(floatOrNA(avg_tot_cls_p))

        lcl_chg_pr_min_p = division(total_local_charge_p,total_local_min_p)
        intl_chg_pr_min_p = division(total_intl_charge_p,total_intl_minutes_p)
        tot_chg_pr_min_p = division(total_charge_p,total_min_p)

        local_charge_per_min_p= str(floatOrNA(lcl_chg_pr_min_p))
        intl_charge_per_min_p= str(floatOrNA(intl_chg_pr_min_p))
        total_charge_per_min_p= str(floatOrNA(tot_chg_pr_min_p))
        
    if output == 1:
        return render_template("predict-result.html", user=current_user,
        churn= "Yes",
        is_churn = churned,

        account_length= account_length_p,
        location_code= location_code_p,
        customer_service_calls= customer_service_calls_p,
        intertiol_plan= intertiol_plan_str,
        voice_mail_plan= voice_mail_plan_str,
        number_vm_messages= number_vm_messages_p,

        total_day_min= total_day_min_p,
        total_day_calls= total_day_calls_p,
        total_day_charge= total_day_charge_p,

        total_eve_min= total_eve_min_p,
        total_eve_calls= total_eve_calls_p,
        total_eve_charge= total_eve_charge_p,
        
        total_night_minutes= total_night_minutes_p,
        total_night_calls= total_night_calls_p,
        total_night_charge= total_night_charge_p,

        total_intl_minutes= total_intl_minutes_p,
        total_intl_calls= total_intl_calls_p,
        total_intl_charge= total_intl_charge_p,
        
        total_local_mins = total_local_min_p,
        total_local_calls = total_local_calls_p,
        total_local_charge = total_local_charge_p,
        
        total_mins = total_min_p,
        total_calls = total_calls_p,
        total_charge = total_charge_p,
        
        avg_local_calls = avg_local_calls_p,
        avg_intl_calls = avg_intl_calls_p,
        avg_total_calls = avg_total_calls_p,

        local_charge_per_min = local_charge_per_min_p,
        intl_charge_per_min = intl_charge_per_min_p,
        total_charge_per_min = total_charge_per_min_p)

    elif output==0:
        return render_template("predict-result.html", user=current_user,
        churn= "No",
        is_churn = not churned,

        account_length= account_length_p,
        location_code= location_code_p,
        customer_service_calls= customer_service_calls_p,
        intertiol_plan= intertiol_plan_str,
        voice_mail_plan= voice_mail_plan_str,
        number_vm_messages= number_vm_messages_p,

        total_day_min= total_day_min_p,
        total_day_calls= total_day_calls_p,
        total_day_charge= total_day_charge_p,

        total_eve_min= total_eve_min_p,
        total_eve_calls= total_eve_calls_p,
        total_eve_charge= total_eve_charge_p,
        
        total_night_minutes= total_night_minutes_p,
        total_night_calls= total_night_calls_p,
        total_night_charge= total_night_charge_p,

        total_intl_minutes= total_intl_minutes_p,
        total_intl_calls= total_intl_calls_p,
        total_intl_charge= total_intl_charge_p,
        
        total_local_mins = total_local_min_p,
        total_local_calls = total_local_calls_p,
        total_local_charge = total_local_charge_p,
        
        total_mins = total_min_p,
        total_calls = total_calls_p,
        total_charge = total_charge_p,
        
        avg_local_calls = avg_local_calls_p,
        avg_intl_calls = avg_intl_calls_p,
        avg_total_calls = avg_total_calls_p,

        local_charge_per_min = local_charge_per_min_p,
        intl_charge_per_min = intl_charge_per_min_p,
        total_charge_per_min = total_charge_per_min_p)

    else:
        return render_template("predict.html", user=current_user,
        churn="Unpreditable",
        is_churn = churned,
        
        account_length= "Undefined",
        location_code= "Undefined",
        customer_service_calls= "Undefined",
        intertiol_plan= "Undefined",
        voice_mail_plan= "Undefined",
        number_vm_messages= "Undefined",

        total_day_min= "Undefined",
        total_day_calls= "Undefined",
        total_day_charge= "Undefined",

        total_eve_min= "Undefined",
        total_eve_calls= "Undefined",
        total_eve_charge= "Undefined",
        
        total_night_minutes= "Undefined",
        total_night_calls= "Undefined",
        total_night_charge= "Undefined",

        total_intl_minutes= "Undefined",
        total_intl_calls= "Undefined",
        total_intl_charge= "Undefined",
        
        total_local_mins = "Undefined",
        total_local_calls = "Undefined",
        total_local_charge = "Undefined",
        
        total_mins = "Undefined",
        total_calls = "Undefined",
        total_charge = "Undefined",
        
        avg_local_calls = "Undefined",
        avg_intl_calls = "Undefined",
        avg_total_calls = "Undefined",

        local_charge_per_min = "Undefined",
        intl_charge_per_min = "Undefined",
        total_charge_per_min = "Undefined")

const ped_form=document.querySelector('#ped_form');
const form1 = document.querySelector('#form1');
const form2 = document.querySelector('#form2');
const form_obj=document.forms.pedigree_form;
const diabetic_obj=document.forms.diabetic_form;
ped_form.addEventListener('submit',(e)=>{
    e.preventDefault();
    let gp_f = form_obj.grandparents_father.value;
    let gp_m = form_obj.grandparents_mother.value;
    let father_diabetic=form_obj.father_diabetic.value;
    let mother_diabetic=form_obj.mother_diabetic.value;
    let siblings_diabetic=form_obj.siblings.value;
    console.log("grand parent father ",gp_f)
    fetch(window.location.origin.toString()+'/health/pedigree', {
        method: 'POST',
        body: JSON.stringify({ grandp_f:gp_f,grandp_m:gp_m,diabetic_father:father_diabetic,diabetic_mother:mother_diabetic,siblings:siblings_diabetic}),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(res => res.json())
        .then(r => {
            console.log(r);
            let pedigree = { pedigree_function:r.pedigree };
            diabetic_obj.Diabetes_PF.value=pedigree.pedigree_function;
        }).catch((error) => {
            console.log('Error', error);
            //textField.value = ''
        });

    form1.style.display="none";
    form2.style.display="block";
    form2.style.opacity="1";
    
})

window.onload=()=>{
    if (window.location.href.includes('result'))
        window.location.href += '#result'
}
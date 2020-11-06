var password = document.getElementById("password")
  , confirm_password = document.getElementById("confirm_password");

function validatePassword(){
  if(password.value != confirm_password.value) {
    confirm_password.setCustomValidity("Passwords Don't Match");
  } else {
    confirm_password.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;


var phone1 = document.getElementById("phone1")
  , phone2 = document.getElementById("phone2")
    ,phone3 = document.getElementById("phone3");

function validatePhone(){
  if(phone1.value == phone2.value) {
    phone2.setCustomValidity("Same Phone Number Given");
  }
  else if(phone1.value == phone3.value || phone2.value == phone3.value)
  {
    phone3.setCustomValidity("Same Phone Number Given");
    phone2.setCustomValidity('');
  }
  else {
    phone2.setCustomValidity('');
    phone3.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

phone1.onchange = validatePhone;
phone2.onkeyup = validatePhone;
phone3.onkeyup = validatePhone;


var err = document.getElementById("email_same");
err.scrollIntoView({behavior: "smooth", block: "center"});

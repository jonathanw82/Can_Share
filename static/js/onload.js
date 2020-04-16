
//when the onclick fuction is called from the age warning modal it adds warning=clicked to the session cookie
function clear_modal(){
    document.cookie = 'warning=clicked' 
}
/* when the document first starts the on ready function looks at the session cookie if there is no 
entry the displays the modal, else it does nothing */
$(document).ready(function () {

 var x = document.cookie;
  var b = x.split(';')
  .map(cookie => cookie.split('='))
  .reduce((accumulator, [key, value]) => 
    ({ ...accumulator, [key.trim()]: decodeURIComponent(value) }), 
    {});
  console.log(b);
  if (b.warning != 'clicked'){
      $("#agewarning").modal('show');
  }
  else{
  };
});







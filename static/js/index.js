

function vote(direction, element) {
    
     var xhttp = new XMLHttpRequest();// xhttp request url passin 1 and can_id  
     xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {// results python going to check if the user has already rated it and determin what action to take
                results = this.responseText;
                console.log(results)
            }
        };
        xhttp.open("GET", '/vote/' + direction + '/' + element.id, true);
        xhttp.send();
        

    if (direction == 'up') {
         
        if ('results' == 1) {
            document.getElementById('thumbsiconup').className =('fas fa-thumbs-up TU');  // if the results are 1 or 0 change the icon from a filled in one to a non filled in one.  
            document.getElementById('thumbsicondown').className =('far fa-thumbs-down TD'); 
        }
        else {
            document.getElementById('thumbsiconup').className =('far fa-thumbs-up TU');
            document.getElementById('thumbsicondown').className =('fas fa-thumbs-down TD');
        }
    }
    else {
         
        if ( 'results' == 0) {
            document.getElementById('thumbsicondown').className =('fas fa-thumbs-up TD');// if the results are 1 or 0 change the icon from a filled in one to a non filled in one.
            document.getElementById('thumbsiconup').className =('far fa-thumbs-up TU');  
        }
        else {
            document.getElementById('thumbsicondown').className =('far fa-thumbs-up TD');
        }
    }

}
// far is not clicked
// fas is clicked

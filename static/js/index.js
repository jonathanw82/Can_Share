
// takes the and id of the can then 
function updatemodal(name, _id) {
    document.getElementById('warning-p').innerHTML = 'You are about to delete ' + name + '!';
    document.getElementById('warning-a').href = '/delete_can/' + _id;
}

function vote(direction, element) {
    
    var xhttp = new XMLHttpRequest();// xhttp request url passin 1 and can_id  
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {// results python going to check if the user has already rated it and determin what action to take
            results = this.responseText;
            console.log(results);
            var test = element.parentElement.id + 'up';
            console.log(test);
            var test2 = element.parentElement.id + 'down';
            if (results == 'up') {
                document.getElementById(test).className = ('fas fa-thumbs-up TU');   
                document.getElementById(test2).className = ('far fa-thumbs-down TD');
            }
            else if (results == 'down') {
                document.getElementById(test).className = ('far fa-thumbs-up TU'); // fill in down and not fillin up
                document.getElementById(test2).className = ('fas fa-thumbs-down TD'); 
            }
            else {
                document.getElementById(test).className = ('far fa-thumbs-up TU');  // dont fill in
                document.getElementById(test2).className = ('far fa-thumbs-down TD');  
            }
        }
    };
    xhttp.open("GET", '/vote/' + direction + '/' + element.parentElement.id, true);
    xhttp.send();

}
// far is not clicked
// fas is clicked

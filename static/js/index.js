
// takes the name and id of the can then displays them in the delete modal
function updatemodal(name, _id) {
    document.getElementById('warning-p').innerHTML = 'You are about to delete ' + name + '!';
    document.getElementById('warning-a').href = '/delete_can/' + _id;
}

function vote(direction, element) {
    
    var xhttp = new XMLHttpRequest();// xhttp request url passing the direction and can_id to vote function in python 
    xhttp.onreadystatechange = function () {
/* results python going to check if the user has already rated it and determin what action to take */
        if (this.readyState == 4 && this.status == 200) {
            results = JSON.parse(this.responseText);
            
            var test = element.parentElement.id + 'up';
            
            var test2 = element.parentElement.id + 'down';
            if (results.direction == 'up') {
                document.getElementById(test).className = ('fas fa-thumbs-up TU'); // fill in up and not fillin down
                document.getElementById(test2).className = ('far fa-thumbs-down TD');
            }
            else if (results.direction == 'down') {
                document.getElementById(test).className = ('far fa-thumbs-up TU'); // fill in down and not fillin up
                document.getElementById(test2).className = ('fas fa-thumbs-down TD'); 
            }
            else {
                document.getElementById(test).className = ('far fa-thumbs-up TU');  // dont fill in either
                document.getElementById(test2).className = ('far fa-thumbs-down TD');  
            }
            console.log(element.parentElement.id);
            document.getElementById(element.parentElement.id + 'score').innerHTML= results.score; // updates the score in the html
        }
    };
    xhttp.open("GET", '/vote/' + direction + '/' + element.parentElement.id, true);
    xhttp.send();

}
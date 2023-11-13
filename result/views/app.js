var app = angular.module('catsvsdogs', []);
var socket = io.connect();

var bg1 = document.getElementById('background-stats-1');
var bg2 = document.getElementById('background-stats-2');

app.controller('statsCtrl', function($scope){
  
  var updateScores = function(){
    socket.on('scores', function (json) {
       data = JSON.parse(json);
       var user1 = data.user1
       var user2 = data.user2
       var option = data.option
       var result = data.result

       $scope.$apply(function () {
         $scope.user1 = user1;
         $scope.user2 = user2;
         $scope.option = option;
         $scope.result = result;
       });
    });
  };

  var init = function(){
    document.body.style.opacity=1;
    updateScores();
  };
  socket.on('message',function(data){
    init();
  });
});
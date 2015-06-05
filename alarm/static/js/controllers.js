var alarmApp = angular.module('alarmApp', ['alarmApp']);



alarmApp.controller('AlarmController', ['$scope', '$http', '$interval', function ($scope, $http, $interval) {
    $http.get('api/status/').success(function(data){
        $scope.alarm = data;
    });
    $scope.sendCommand = function(command){
        if (command === 'ARM' || command === 'DISARM'){
            var action = {'action': command};
            $http.post('/', action).success(function (data){
                $scope.alarm = data
            });
        }
    };
    $scope.update = function(){
        $interval(function(){
            $http.get('api/status/').success(function(data){
                $scope.alarm = data;
            });
        }, 10000)
    };
    $scope.update();
}]);
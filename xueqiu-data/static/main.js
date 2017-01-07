(function () {

  'use strict';

  angular.module('XueqiuholdApp', [])

  .controller('XueqiuholdController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {

    $scope.submitButtonText = 'Submit';
    $scope.loading = false;
    $scope.urlerror = false;

    $scope.getResults = function() {

      $log.log('test');

      // get the URL from the input
      var userInput = $scope.url;

      // fire the API request
      $http.post('/start', {'url': userInput}).
        success(function(results) {
          $log.log(results);
          getXueqiuHold();
          $scope.xueqiuhold = null;
          $scope.trans = null;
          $scope.loading = true;
          $scope.submitButtonText = 'Loading...';
          $scope.urlerror = false;
        }).
        error(function(error) {
          $log.log(error);
        });

    };

    function getXueqiuHold() {

      var timeout = '';

      var poller = function() {
        // fire another request
        $http.get('/data').
          success(function(data, status, headers, config) {
            if(status === 202) {
              $log.log(data, status);
            } else if (status === 200){
              $log.log(data);
              $scope.loading = false;
              $scope.submitButtonText = "Submit";
              $scope.xueqiuhold = data;
                $http.get('/trans1').
                  success(function(data, status, headers, config) {
                    if(status === 202) {
                      $log.log(data, status);
                    } else if (status === 200){
                      $log.log(data);
                      $scope.trans = data;
              }});
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 2000);
          }).
          error(function(error) {
            $log.log(error);
            $scope.loading = false;
            $scope.submitButtonText = "Submit";
            $scope.urlerror = true;
          });
      };

      poller();

    }

  }])

  .directive('wordcountChart', ['$parse', function ($parse) {
    return {
      restrict: 'E',
      replace: true,
      template: '<div id="chart"></div>',
      link: function (scope) {
        scope.$watch('xueqiuhold', function() {
          d3.select('#chart').selectAll('*').remove();
          var data = scope.xueqiuhold;
          for (var word in data) {
            d3.select('#chart')
              .append('div')
              .selectAll('div')
              .data(word[0])
              .enter()
              .append('div')
              .style('width', function() {
                return (data[word]*3) + 'px';
              })
              .text(function(d){
                return word;
              });
          }
        }, true);
      }
     };
  }]);

}());

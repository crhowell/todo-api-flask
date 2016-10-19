'use strict';

angular.module('todoListApp')
.directive('todo', function(){
  return {
    templateUrl: '/static/templates/todo.html',
    replace: true,
    controller: 'todoCtrl'
  }
});
function Game(winner, loser, score, date) {
  this.winner = winner;
  this.loser = loser;
  this.score = score;
  this.date = date;
}

function Person(name) {
  this.name = name;
  this.score = BASE;
  this.wins = 0;
  this.losses = 0;
}

$.extend(Person.prototype, {
  reset: function() {
    this.score = BASE;
    this.wins = 0;
    this.losses = 0;
  },
  url: function() {
    return '../user/' + this.name + '/';
  }
});

var people = [],
  gameList = [],

  BASE = 1500,

  HIGH_K = 32,
  MED_K = 24,
  LOW_K = 16,

  K_HIGH_CUTOFF = 2400,
  K_LOW_CUTOFF = 2100,

  rows,
  games,
  curGame;

function sortByScore() {
  people.sort(function(a, b) {
    return b.score - a.score;
  });
}

function getPerson(name) {
  for(var a = 0; a < people.length; a++) {
    if(people[a].name == name) {
      return people[a];
    }
  }
}

function calculate(matches) {
  _.each(matches, function(match) {

    if(!getPerson(match.winner)) {
      people.push(new Person(match.winner));
    }
    if(!getPerson(match.loser)) {
      people.push(new Person(match.loser));
    }
  });

  /* reset in case this isn't the first run through */
  $.each(people, function() {
    this.reset();
  });

//  curGame = 0;
//  games = $(rows.get().reverse());
  gameList = [];
  for (var i = 0; i < matches.length; i++) {
    gameList.push(lookAtNextGame(matches[i]));
  }
  makeGrid();
}

function makeGrid(byPoints) {
  sortByScore();
  $('.odds_grid').remove();
  var table = $('<table class="odds_grid"></table>');
  var header = $('<tr class="odds_header"></tr>');

  header.append(
    $('<th class="grid_toggle" title="Toggle strength/points"></th>')
      .text(byPoints ? 'points on win' : '% chance of win')
      .click(function() {
        makeGrid(!byPoints);
      })
  );

  $.each(people, function(lp) {
    var lp = this;
    var row = $('<tr></tr>');
    header.append('<th><div>' + lp.name + '</div></th>');
    $.each(people, function(tp) {
      var tp = this;
      var strength = strengthStr = '' + Math.round((calcExpected(lp.score, tp.score)) * 100);
      var points = Math.round(getK(lp.score) * (1 - calcExpected(lp.score, tp.score)));
      if(strengthStr.length == 1) strengthStr = '0' + strengthStr;
      var cell = $('<td style="background-color:rgba(0,255,0,0.' + strengthStr + ');"></td>');
      cell.data('player1', lp);
      cell.data('player2', tp);
      cell.text((lp == tp ? '-' : (byPoints ? points : strength)));
      row.append(cell);
    });
    row.prepend('<th><a href="' + lp.url() + '">' + lp.name + ' (' + Math.round(lp.score) + ') ' + lp.wins + ' - ' + lp.losses + '</a></th>');
    table.append(row);
  });

  table.prepend(header);
  table.appendTo($('#OidrGrid'));

  table.find('td').on('mouseover', function() {
    if($(this).text() == '-') {
      return;
    }

    if(!$(this).hasClass('showdown')) {
      showShowdown($(this).data('player1'), $(this).data('player2'));
    }
  }).on('mouseout', function() {
      $(this).removeClass('showdown');
      $('#showdown').remove();
  });
}

function showShowdown(player1, player2) {
  $("#showdown").remove();
  var showdown = $('<div id="showdown"></div>').appendTo($(document.body));
  var relGames = [];
  $.each(gameList, function() {
    if((this.winner == player1 && this.loser == player2) || (this.winner == player2 && this.loser == player1)) {
      relGames.push(this);
    }
  });
  var player1wins = 0, player2wins = 0;
  var gameDisplay = $('<div></div>');
  $.each(relGames, function() {
    if(this.winner == player1) {
      player1wins++;
    } else {
      player2wins++;
    }
    var gameRow = $('<div></div>').text(this.winner.name + ' beat ' + this.loser.name + ' ' + (this.date.getMonth() + 1) + '/' + this.date.getDate() + ': ' + this.score);
    gameDisplay.append(gameRow);
  });
  var totalgames = player1wins + player2wins;
  var title = $('<div class="title"></div>').text(player1.name + ' (' + player1wins + ') vs ' + player2.name + ' (' + player2wins + ')');
  var desc = $('<div></div>');
  if(totalgames == 0) {
    desc.text('no recorded matches');
  } else {
    var expected = Math.round((calcExpected(player1.score, player2.score)) * 100);
    var actual = Math.round(player1wins / totalgames * 100);
    desc.text('expected ' + expected + '%, actual ' + actual + '%.')
  }
  showdown.append(title, desc, gameDisplay);
}

function getK(rating) {
  if(rating > K_HIGH_CUTOFF) {
    return LOW_K;
  } else if(rating > K_LOW_CUTOFF) {
    return MED_K;
  } else {
    return HIGH_K;
  }
}

function calcExpected(selfRating, otherRating) {
  return 1/(1+Math.pow(10, (otherRating - selfRating) / 400));
}

/* returns a date object for a string */
function parseDate(str) {
  if(str.indexOf(':') === -1) {
    str = str.replace(/( .\.m\.)/, ':00$1');
  }
  return new Date(str.replace('.', ''));
}

function lookAtNextGame(match) {
  var winner = getPerson(match.winner);
  var loser = getPerson(match.loser);
  var score = match.results;
  var dt = new Date(match.timestamp);
  var hours = '' + dt.getHours(), minutes = '' + dt.getMinutes();
  if(hours.length == 1) hours = '' + 0 + hours;
  if(minutes.length == 1) minutes = '' + 0 + minutes;

//  dateCell.text(dt.getMonth() + 1 + '/' + dt.getDate() + ' ' + hours + ':' + minutes);

//  gameList.push(new Game(winner, loser, score, dt));

  var winnerStrength = calcExpected(winner.score, loser.score);
  var loserStrength = calcExpected(loser.score, winner.score);

  var winnerChange = getK(winner.score) * (1 - winnerStrength);
  var loserChange = getK(loser.score) * (0 - loserStrength);

  var gameStrength = winnerChange / HIGH_K;
//
//  row.find('.awarded_points').remove();
//  row.append('<td class="awarded_points"><span>' + Math.round(winnerChange) + '</span>&nbsp;<span>' + Math.round(loserChange) + '</span></td>');
//
//  row.find('.remove_match').remove();
//  row.append($('<td class="remove_match"><a href="#">X</a></td>').click(function() {
//    $(this).parent().toggleClass('disabled');
//    calculate();
//    return false;
//  }));
  winner.score += winnerChange;
  loser.score += loserChange;

  winner.wins++;
  loser.losses++;

  var rowA = '' + Math.round(gameStrength * 100);
  if(rowA.length == 1) {
    rowA = '0' + rowA;
  }

//  row.css('background-color', 'rgba(0,255,0,0.' + rowA + ')');

  return new Game(winner, loser, score, dt);
}

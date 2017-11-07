$(document).ready(function() {

  var options = {xaxis:{font:{}},yaxis:{font:{}},grid:{},lines:{},points:{}};
  options.xaxis.font.size   = 10;
  options.xaxis.font.color  = '#333';
  options.xaxis.tickSize    = 10;
  options.xaxis.min         = 2400;
  options.xaxis.max         = 2480;
  options.yaxis.font.size   = 10;
  options.yaxis.font.color  = '#333';
  options.yaxis.tickSize    = 10;
  options.yaxis.min         = -110;
  options.yaxis.max         = -40;
  options.grid.borderWidth  = 1.0;
  options.grid.labelMargin  = 10;
  options.grid.color        = '#c0c0c0';
  options.lines.lineWidth   = 1.2;
  options.shadowSize        = 0;


  $.plot('#chart', [[0, 0]], options);

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  var colorToggle  = {},
      clients      = undefined,
      clientActive = undefined,
      nameTemp     = undefined;


  socket.on('render_clients', function(data) {
    if(clients != JSON.stringify(data.data)) {
      $('#clients').empty();
      for(var i = 0; i < data.data.length; i++) {
        var host     = data.data[i].h,
            hostSel  = data.data[i].h.replace(/\./g, '-'),
            name     = data.data[i].n,
            osName   = data.data[i].os,
            qty      = data.data[i].q;

        if(clientActive == undefined) {
          clientActive = hostSel;
        }

        $('#clients').append(
          '<div class="item client ' + hostSel + ' rebuild">' +
            '<div class="id">' +
              '<div class="mark"><span></span></div>' +
              '<div class="module-counter"><i>[</i><span>' + qty + '</span><i>]</i></div>' +
              '<div class="name">' +
                '<span class="name-text">' + name + '</span>' +
                '<div class="field">' +
                  '<input type="text" placeholder="' + name + '">' +
                  '<i class="fa fa-check confirm-name" aria-hidden="true"></i>' +
                '</div>' +
              '</div>' +
            '</div>' +
            '<p class="details" title="">' +
              '<span class="address">' + host + '</span> ' +
              '<span class="system">(' + osName + ')</span>' +
            '</p>' +
            '<div class="overlay"></div>' +
          '</div>'
        );
      }
      $('#clients .item.' + hostSel).addClass('active');

      clients = JSON.stringify(data.data);
    }
  });


  socket.on('render_modules', function(data) {
    if($('#clients .item').hasClass(data.data.h.replace(/\./g,'-'))) {
      var hostSel = data.data.h.replace(/\./g,'-');

      $('.client.' + hostSel + ' .module-counter span').html(data.data.q);
      if(data.data.r || $('.client.' + hostSel).hasClass('rebuild')) {
        $('#modules').empty()
        for(var i = 0; i < data.data.q; i++) {
          var module = JSON.parse(data.data.d[0][i]),
              colors = data.data.d[1][i][0],
              cIndex = parseInt(data.data.d[1][i][1]) + 1;
              colorToggle[module.s] = 1;

          $('#modules').append(
            '<div class="item module ' + module.s + '">' +
              '<div class="port" style="color: ' + colors[cIndex - 1] + ';">' + module.p + '</div>' +
              '<div class="serial">' + module.s + '</div>' +
              '<div class="package">' +
                '<span>' + module.pr + '</span><span>/</span><span>' + module.pn + '</span>' +
              '</div>' +
              '<div class="time">' + module.t + '</div>' +
              '<div class="conf">' +
                '<div class="color">' +
                  '<span class="cl-item" style="background-color: ' + colors[0] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[1] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[2] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[3] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[4] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[5] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[6] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[7] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[8] + ';">c</span>' +
                  '<span class="cl-item" style="background-color: ' + colors[9] + ';">c</span>' +
                '</div>' +
                '<div class="chart">' +
                  '<span class="ch-item" data-value="0">1</span>' +
                  '<span class="ch-item" data-value="10">10</span>' +
                  '<span class="ch-item" data-value="100">100</span>' +
                  '<span class="ch-item" data-value="1">ALL</span>' +
                '</div>' +
              '</div>' +
            '</div>'
          );

          $('#modules .' + module.s + ' .ch-item[data-value=' + module.ct + ']').addClass('active');
          $('#modules .' + module.s + ' .cl-item:nth-child(' + cIndex + ')').addClass('active');
        }
        $('.client.' + hostSel).removeClass('rebuild');
      } else {
        if(data.data.d[0].length != 0) {
          for(var i = 0; i < data.data.q; i++) {
            try {
              var module = JSON.parse(data.data.d[0][i]);
              $('#modules .' + module.s + ' .package span:first-child').html(module.pr)
              $('#modules .' + module.s + ' .package span:last-child').html(module.pn)
              $('#modules .' + module.s + ' .time').html(module.t)
            } catch(e) {
              continue;
            }
          }
        } else {
          $('#modules').empty();
          $('#modules').append(
            '<div class="item module no-connected">No connected modules</div>'
          );
        }
      }

      var chart = [];
      if(data.data.d[0].length != 0) {
        for(var i = 0; i < data.data.d[0].length; i++) {
          var module = JSON.parse(data.data.d[0][i]);

          if(colorToggle[module.s]) {
            moduleChart = module.c;
          } else {
            moduleChart = [[0, 0]];
          }

          chart.push({
            data: moduleChart,
            color: data.data.d[1][i][0][data.data.d[1][i][1]]
          });
        }
      } else {
        chart = [[0, 0]]
      }

      $.plot('#chart', chart, options);
    }
  });


  $('#client-side').on('click', function(e) {
    var target = $(e.target);

    if(target.hasClass('overlay')) {
      if(!target.parents('.client').hasClass('active')) {
        $('#clients > .item').removeClass('active');
        $('#clients > .item .id .name i').removeClass('fa-circle').addClass('fa-circle-thin');
        $(target.parents('.client').addClass('active').addClass('rebuild'));
        $(target.parents('.client').find('.name i').removeClass('fa-circle-thin').addClass('fa-circle'));
      }
    }

    if(target.attr('id') == 'conf-btn') {
      if($('#modules').hasClass('conf-on')) {
        target.removeClass('fa-times').removeClass('active').addClass('fa-cog');
        $('#modules').removeClass('conf-on');
      } else {
        target.removeClass('fa-cog').addClass('fa-times').addClass('active');
        $('#modules').addClass('conf-on');
      }
    }

    if(target.hasClass('name-text')) {
      if(!$('.client.active .id .name').hasClass('edit')) {
        $('.client.active .id .name').addClass('edit');
      }
    }

    if(target.hasClass('confirm-name')) {
      var name = target.prev().val(),
          host = $('.client.active').attr('class').split(' ')[2].replace(/-/g, '.');

      socket.emit('set_name', [host, name]);
      $('.client.active .id .name').removeClass('edit');
    }

    if(target.hasClass('port')) {
      var hostSelector = $('.client.active').attr('class').split(' ')[2],
          serial       = target.parents('.item').attr('class').split(' ')[2];

      if(target.hasClass('off')) {
        colorToggle[serial] = 1;
        target.removeClass('off');
      } else {
        colorToggle[serial] = 0;
        target.addClass('off');
      }
    }

    if(target.hasClass('cl-item')) {
      if(!target.hasClass('active')) {
        var serial = target.parents('.item').attr('class').split(' ')[2],
            index  = target.index();
            host   = $('.client.active').attr('class').split(' ')[2].replace(/-/g, '.');

        socket.emit('set_color', [host, JSON.stringify({"s": serial, "i": index})])

        $('.' + serial + ' .color .cl-item').removeClass('active');
        $(target).addClass('active');
      }
    }

    if(target.hasClass('ch-item')) {
      if(!target.hasClass('active')) {
        var serial    = target.parents('.item').attr('class').split(' ')[2],
            chartType = target.attr('data-value'),
            host      = $('.client.active').attr('class').split(' ')[2].replace(/-/g, '.');

        socket.emit('set_chart_type', [host, JSON.stringify({"s": serial, "t": chartType})])

        $('.' + serial + ' .chart .ch-item').removeClass('active');
        $(target).addClass('active');
      }
    }
  });

});
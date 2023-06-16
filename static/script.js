var status_check_timer;

// Generated from:
// for c in colour.RGB_TO_COLOR_NAMES:
//    print("  ['{}', '{}', '{}', '{}', '{}'],".format(colour.RGB_TO_COLOR_NAMES[c][0], c[0], c[1], c[2], colour.Color(rgb=(c[0]/255, c[1]/255, c[2]/255)).hex))
//
const color_list = [
  ['Black', '0', '0', '0', '#000'],
  ['Navy', '0', '0', '128', '#000080'],
  ['DarkBlue', '0', '0', '139', '#00008b'],
  ['MediumBlue', '0', '0', '205', '#0000cd'],
  ['Blue', '0', '0', '255', '#00f'],
  ['DarkGreen', '0', '100', '0', '#006400'],
  ['Green', '0', '128', '0', '#008000'],
  ['DarkCyan', '0', '139', '139', '#008b8b'],
  ['DeepSkyBlue', '0', '191', '255', '#00bfff'],
  ['DarkTurquoise', '0', '206', '209', '#00ced1'],
  ['MediumSpringGreen', '0', '250', '154', '#00fa9a'],
  ['Lime', '0', '255', '0', '#0f0'],
  ['SpringGreen', '0', '255', '127', '#00ff7f'],
  ['Cyan', '0', '255', '255', '#0ff'],
  ['MidnightBlue', '25', '25', '112', '#191970'],
  ['DodgerBlue', '30', '144', '255', '#1e90ff'],
  ['LightSeaGreen', '32', '178', '170', '#20b2aa'],
  ['ForestGreen', '34', '139', '34', '#228b22'],
  ['SeaGreen', '46', '139', '87', '#2e8b57'],
  ['DarkSlateGray', '47', '79', '79', '#2f4f4f'],
  ['LimeGreen', '50', '205', '50', '#32cd32'],
  ['MediumSeaGreen', '60', '179', '113', '#3cb371'],
  ['Turquoise', '64', '224', '208', '#40e0d0'],
  ['RoyalBlue', '65', '105', '225', '#4169e1'],
  ['SteelBlue', '70', '130', '180', '#4682b4'],
  ['DarkSlateBlue', '72', '61', '139', '#483d8b'],
  ['MediumTurquoise', '72', '209', '204', '#48d1cc'],
  ['Indigo', '75', '0', '130', '#4b0082'],
  ['DarkOliveGreen', '85', '107', '47', '#556b2f'],
  ['CadetBlue', '95', '158', '160', '#5f9ea0'],
  ['CornflowerBlue', '100', '149', '237', '#6495ed'],
  ['MediumAquamarine', '102', '205', '170', '#66cdaa'],
  ['DimGray', '105', '105', '105', '#696969'],
  ['SlateBlue', '106', '90', '205', '#6a5acd'],
  ['OliveDrab', '107', '142', '35', '#6b8e23'],
  ['SlateGray', '112', '128', '144', '#708090'],
  ['LightSlateGray', '119', '136', '153', '#789'],
  ['MediumSlateBlue', '123', '104', '238', '#7b68ee'],
  ['LawnGreen', '124', '252', '0', '#7cfc00'],
  ['Chartreuse', '127', '255', '0', '#7fff00'],
  ['Aquamarine', '127', '255', '212', '#7fffd4'],
  ['Maroon', '128', '0', '0', '#800000'],
  ['Purple', '128', '0', '128', '#800080'],
  ['Olive', '128', '128', '0', '#808000'],
  ['Gray', '128', '128', '128', '#808080'],
  ['LightSlateBlue', '132', '112', '255', '#8470ff'],
  ['SkyBlue', '135', '206', '235', '#87ceeb'],
  ['LightSkyBlue', '135', '206', '250', '#87cefa'],
  ['BlueViolet', '138', '43', '226', '#8a2be2'],
  ['DarkRed', '139', '0', '0', '#8b0000'],
  ['DarkMagenta', '139', '0', '139', '#8b008b'],
  ['SaddleBrown', '139', '69', '19', '#8b4513'],
  ['DarkSeaGreen', '143', '188', '143', '#8fbc8f'],
  ['LightGreen', '144', '238', '144', '#90ee90'],
  ['MediumPurple', '147', '112', '219', '#9370db'],
  ['DarkViolet', '148', '0', '211', '#9400d3'],
  ['PaleGreen', '152', '251', '152', '#98fb98'],
  ['DarkOrchid', '153', '50', '204', '#9932cc'],
  ['YellowGreen', '154', '205', '50', '#9acd32'],
  ['Sienna', '160', '82', '45', '#a0522d'],
  ['Brown', '165', '42', '42', '#a52a2a'],
  ['DarkGray', '169', '169', '169', '#a9a9a9'],
  ['LightBlue', '173', '216', '230', '#add8e6'],
  ['GreenYellow', '173', '255', '47', '#adff2f'],
  ['PaleTurquoise', '175', '238', '238', '#afeeee'],
  ['LightSteelBlue', '176', '196', '222', '#b0c4de'],
  ['PowderBlue', '176', '224', '230', '#b0e0e6'],
  ['Firebrick', '178', '34', '34', '#b22222'],
  ['DarkGoldenrod', '184', '134', '11', '#b8860b'],
  ['MediumOrchid', '186', '85', '211', '#ba55d3'],
  ['RosyBrown', '188', '143', '143', '#bc8f8f'],
  ['DarkKhaki', '189', '183', '107', '#bdb76b'],
  ['Silver', '192', '192', '192', '#c0c0c0'],
  ['MediumVioletRed', '199', '21', '133', '#c71585'],
  ['IndianRed', '205', '92', '92', '#cd5c5c'],
  ['Peru', '205', '133', '63', '#cd853f'],
  ['VioletRed', '208', '32', '144', '#d02090'],
  ['Chocolate', '210', '105', '30', '#d2691e'],
  ['Tan', '210', '180', '140', '#d2b48c'],
  ['LightGray', '211', '211', '211', '#d3d3d3'],
  ['Thistle', '216', '191', '216', '#d8bfd8'],
  ['Orchid', '218', '112', '214', '#da70d6'],
  ['Goldenrod', '218', '165', '32', '#daa520'],
  ['PaleVioletRed', '219', '112', '147', '#db7093'],
  ['Crimson', '220', '20', '60', '#dc143c'],
  ['Gainsboro', '220', '220', '220', '#dcdcdc'],
  ['Plum', '221', '160', '221', '#dda0dd'],
  ['Burlywood', '222', '184', '135', '#deb887'],
  ['LightCyan', '224', '255', '255', '#e0ffff'],
  ['Lavender', '230', '230', '250', '#e6e6fa'],
  ['DarkSalmon', '233', '150', '122', '#e9967a'],
  ['Violet', '238', '130', '238', '#ee82ee'],
  ['LightGoldenrod', '238', '221', '130', '#eedd82'],
  ['PaleGoldenrod', '238', '232', '170', '#eee8aa'],
  ['LightCoral', '240', '128', '128', '#f08080'],
  ['Khaki', '240', '230', '140', '#f0e68c'],
  ['AliceBlue', '240', '248', '255', '#f0f8ff'],
  ['Honeydew', '240', '255', '240', '#f0fff0'],
  ['Azure', '240', '255', '255', '#f0ffff'],
  ['SandyBrown', '244', '164', '96', '#f4a460'],
  ['Wheat', '245', '222', '179', '#f5deb3'],
  ['Beige', '245', '245', '220', '#f5f5dc'],
  ['WhiteSmoke', '245', '245', '245', '#f5f5f5'],
  ['MintCream', '245', '255', '250', '#f5fffa'],
  ['GhostWhite', '248', '248', '255', '#f8f8ff'],
  ['Salmon', '250', '128', '114', '#fa8072'],
  ['AntiqueWhite', '250', '235', '215', '#faebd7'],
  ['Linen', '250', '240', '230', '#faf0e6'],
  ['LightGoldenrodYellow', '250', '250', '210', '#fafad2'],
  ['OldLace', '253', '245', '230', '#fdf5e6'],
  ['Red', '255', '0', '0', '#f00'],
  ['Magenta', '255', '0', '255', '#f0f'],
  ['DeepPink', '255', '20', '147', '#ff1493'],
  ['OrangeRed', '255', '69', '0', '#ff4500'],
  ['Tomato', '255', '99', '71', '#ff6347'],
  ['HotPink', '255', '105', '180', '#ff69b4'],
  ['Coral', '255', '127', '80', '#ff7f50'],
  ['DarkOrange', '255', '140', '0', '#ff8c00'],
  ['LightSalmon', '255', '160', '122', '#ffa07a'],
  ['Orange', '255', '165', '0', '#ffa500'],
  ['LightPink', '255', '182', '193', '#ffb6c1'],
  ['Pink', '255', '192', '203', '#ffc0cb'],
  ['Gold', '255', '215', '0', '#ffd700'],
  ['PeachPuff', '255', '218', '185', '#ffdab9'],
  ['NavajoWhite', '255', '222', '173', '#ffdead'],
  ['Moccasin', '255', '228', '181', '#ffe4b5'],
  ['Bisque', '255', '228', '196', '#ffe4c4'],
  ['MistyRose', '255', '228', '225', '#ffe4e1'],
  ['BlanchedAlmond', '255', '235', '205', '#ffebcd'],
  ['PapayaWhip', '255', '239', '213', '#ffefd5'],
  ['LavenderBlush', '255', '240', '245', '#fff0f5'],
  ['Seashell', '255', '245', '238', '#fff5ee'],
  ['Cornsilk', '255', '248', '220', '#fff8dc'],
  ['LemonChiffon', '255', '250', '205', '#fffacd'],
  ['FloralWhite', '255', '250', '240', '#fffaf0'],
  ['Snow', '255', '250', '250', '#fffafa'],
  ['Yellow', '255', '255', '0', '#ff0'],
  ['LightYellow', '255', '255', '224', '#ffffe0'],
  ['Ivory', '255', '255', '240', '#fffff0'],
  ['White', '255', '255', '255', '#fff'],
]
// noinspection JSUnusedGlobalSymbols
var animation_modes = [];

function ajaxRequest(url) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);

    xhr.onload = function () {

        if (xhr.status !== 200) {
            console.log('Request failed.  Returned status of: ' + xhr.status);
        } else {
            //console.log('Response Text: ' + xhr.responseText);
            document.getElementById("status").innerHTML = "URL: '" + url + "'<br/>Status: " + xhr.response;
//            document.getElementById('led_results').innerHTML = xhr.responseText;
            clearTimeout(status_check_timer);
            check_state()
        }
    };
    try {
        xhr.send();
        console.log('function status: ' + url.slice(1).toUpperCase());
        document.getElementById("status").innerHTML = "URL: '" + url + "'";
    } catch (e) {
        console.log(e)
    }
}

// noinspection JSUnusedGlobalSymbols
function goto(url) {
    location.href = url;
}

function add_color_clickers() {
    var holder = document.getElementById('color_picker')
    for (c in color_list) {
        color = color_list[c]
        color_name = color[0]
        var colSpan = document.createElement('span')
        colSpan.innerHTML = '⬤';
        colSpan.title = 'Set all leds to: ' + color_name
        colSpan.style.backgroundColor = color[4];
        colSpan.style.padding = ".5em";
        colSpan.style.display = "inline-block";

        colSpan.style.cursor = "pointer";
        colSpan.colors = {name:color_name, r: color[1], g: color[2], b: color[3]}
        colSpan.onclick = function(e) {
            var target = e.target || window.event.srcElement;
            ajaxRequest('/color/' + target.colors.name)
        }
        holder.appendChild(colSpan)
    }
}

function setupIndexPage() {
    try {
        $('#rainbowBtn').on('click', function(){ajaxRequest('/rainbow')})
        $('#stopBtn').on('click', function(){ajaxRequest('/all off')})

        add_color_clickers()
        status_check_timer = setTimeout(check_state, 1000);

        $( ".dropdownModeButton" ).change(function() {
            var selected = this.options[this.selectedIndex].value;
            ajaxRequest('/mode/' + selected);
    });

    } catch (e) {
        console.log(e)
    }
}

mqtt_status_color = 'black';
function check_state() {
// Pulls in a JSON object on the state of the pi and lights

    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/state');

    xhr.onload = function () {
        // Check if we got 'true' as a response
        if (xhr.status == 200) {
            state = JSON.parse(xhr.responseText)

            // Set MQTT light state
            if (state.mqtt_status == 'connected') {
                mqtt_status_color = 'green';
            } else if (state.mqtt_status == 'disconnected') {
                mqtt_status_color = 'red';
            } else if (state.mqtt_status == 'not initialized') {
                mqtt_status_color = 'black';
            }

            var anim_modes_from_xhr = state.modes;
            if (animation_modes.length != anim_modes_from_xhr.length) {
                animation_modes = anim_modes_from_xhr;
                //Likely the list of modes changed, rebuild the drop down
                var $picker = $('.dropdownModeButton');
                $picker.empty(); //children().remove();
                for (mode in anim_modes_from_xhr) {
                    mode_name = anim_modes_from_xhr[mode]
                    $picker.append(
                        $('<option/>')
                            .attr('value', mode_name).text(toTitleCase(mode_name)));
                }

            }

            set_light_status(state.strands);
        }
    };
    try {
        xhr.send();
    } catch (e) {
        console.log(e)
        mqtt_status_connected = false;
    }

    //If it's 'not initialized', stop checking
    document.getElementById('mqtt_status').style.color = mqtt_status_color;
    if (mqtt_status_color=='black'){
        document.getElementById('mqtt_status').title = 'MQTT Connection Never Initialized';
    } else if (mqtt_status_color=='green') {
        document.getElementById('mqtt_status').title = 'MQTT Connected and listening';
    } else if (mqtt_status_color=='red') {
        document.getElementById('mqtt_status').title = 'MQTT Disconnected';
    }
    status_check_timer = setTimeout(check_state, 5000);
}

function toTitleCase(str) {
    return str.replace(/(?:^|\s)\w/g, function(match) {
        return match.toUpperCase();
    });
}

function clearBox(div) {
    while(div.firstChild) {
        div.removeChild(div.firstChild);
    }
}
function set_light_status(strands) {
    var holder = document.getElementById('led_results');
    clearBox(holder);

    for (strand_id in strands) {
        var strand = strands[strand_id];
        var strand_div = document.createElement('div')
        strand_div.innerHTML = strand_id;
        strand_div.title = "Strand: " + strand.strand_name + ", pin: " + strand.strand_info.pin;
        strand_div.style.padding = "6px";

        for (led_id in strand.led_info) {
            var led_data = strand.led_info[led_id];
            var led_span = document.createElement('span')
            led_span.innerHTML = '⬤';
            led_span.style.color = led_data.color;
            led_span.title = '[' + led_id + '], Name: ' + led_data.name + ', Current Color: [' + led_data.color + '], Animation Text: ' + led_data.animation_text;

            strand_div.appendChild(led_span);

            if (parseInt(led_id) % 30 == 29) {
                var led_span = document.createElement('span')
                led_span.innerHTML = ' ';
                strand_div.appendChild(led_span);
            }
        }
        holder.appendChild(strand_div);
    }
}

function setupServicePage() {
    try {
        document.getElementById('homeBtn').setAttribute('onclick', "goto('/',)");
        document.getElementById('dashboardBtn').setAttribute('onclick', "window.open('../dashboard')");
        document.getElementById('rebootBtn').setAttribute('onclick', "ajaxRequest('/reboot')");

        try {
            for (const id in serviceLabels) {
                document.getElementById(id).innerHTML = serviceLabels[id].toUpperCase();
            }
        } catch (e) {
            console.log(e)
        }
    } catch (e) {
        console.log(e)
    }
}

window.onload = function () {
    try {
        if (window.name === 'index') {
            setupIndexPage();
        }
        if (window.name === 'service') {
            setupServicePage();
        }
    } catch (e) {
        console.log(e)
    }
};

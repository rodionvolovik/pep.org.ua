$(function() {
    var preview_style = [{
        selector: "edge",
        style: {
            "curve-style": "bezier",
            width: 1
        }
    }, {
        selector: 'node',
        style: {
            "content": "",
            "font-size": 20,
            "ghost": "yes",
            "text-wrap": "wrap",
            "text-max-width": 100,
            "text-valign": "bottom",
            "text-halign": "center",
            "width": 60,
            "height": 60,
            color: "#FAFAFA"
        }
    }, {
        selector: 'node[model="person"]',
        style: {
            "background-image": "/static/images/cytoscape/person.png",
            "background-fit": "contain",
            "background-color": "white",
            "border-width": "1px",
            "border-color": "silver"
        }
    }, {
        selector: 'node[model="company"]',
        style: {
            "background-image": "/static/images/cytoscape/company.png",
            "background-fit": "contain",
            "background-color": "#a9cce3"
        }
    }, {
        selector: 'node.hover',
        style: {
            "text-background-color": "#265eb7",
            "text-background-opacity": 0.8,
            "text-background-shape": "roundrectangle",
            "text-background-padding": "3px",
            "z-index": 100,
            content: "data(name)"
        }
    }, {
        selector: 'node[?is_pep]',
        style: {
            "width": 70,
            "height": 70,
            "border-width": "3px",
            "border-color": "red",
            "background-color": "#76d7c4",
            "background-image": "/static/images/cytoscape/pep_person.png"
        }
    }, {
        selector: 'node[?state_company]',
        style: {
            "width": 70,
            "height": 70,
            "border-width": "3px",
            "border-color": "green",
            "background-color": "yellow",
            "background-image": "/static/images/cytoscape/state_company.png"
        }
    }, {
        selector: 'node[?is_main]',
        style: {
            "width": 80,
            "height": 80,
            "text-background-color": "#265eb7",
            "text-background-opacity": 0.8,
            "text-background-shape": "roundrectangle",
            "text-background-padding": "3px",
            content: "data(name)",
            "z-index": 90
        }
    }];
    var full_style = preview_style.concat([{
        selector: 'node',
        style: {
            "content": "data(name)",
            "color": "#666666",
            "min-zoomed-font-size": 18,
            "font-size": 12
        }
    }, {
        selector: 'node[?is_main]',
        style: {
            "width": 80,
            "height": 80,
            "color": "#444444",
            "text-background-color": "white",
            "text-background-opacity": 0,
            content: "data(name)",
            "z-index": 90
        }
    }, {
        selector: "edge",
        style: {
            width: "mapData(importance, 0, 100, 0.5, 5)"
        }
    }, {
        selector: "edge.hover",
        style: {
            label: "data(relation)",
            "text-wrap": "wrap",
            "text-max-width": 100,
            "color": "#666666",
            "font-size": 10,
            "min-zoomed-font-size": 10,
            "text-background-color": "white",
            "z-index": 140,
            "text-background-opacity": 0.8,
            "text-background-shape": "roundrectangle"
        }
    }, {
        selector: "edge.active",
        style: {
            "line-color": "red"
        }
    }, {
        selector: 'edge[model="person2person"]',
        style: {
            "line-style": "dashed"
        }
    }]);

    function init_preview(elements) {
        var cy_preview = cytoscape({
            userPanningEnabled: false,
            autoungrabify: true,
            container: $('#cy-preview'),
            elements: elements,
            layout: {
                name: 'cose',
                quality: 'default'
            },
            style: preview_style
        }).on('mouseover', 'node', function(event) {
            event.target.addClass("hover");
        }).on('mouseout', 'node', function(event) {
            event.target.removeClass("hover");
        });
    }

    var makeTippy = function(node, text){
        return tippy( node.popperRef(), {
            content: function(){
                var div = document.createElement('div');

                div.innerHTML = text;

                return div;
            },
            trigger: 'manual',
            arrow: false,
            placement: 'top',
            hideOnClick: false,
            multiple: true,
            distance: 0,
            interactive: true,
            animateFill: false,
            theme: "pep",
            sticky: true
        } );
    };

    function init_full(elements) {
        var cy_full = cytoscape({
                container: $('.cy-full'),
                elements: elements,
                style: full_style
            }),
            partial_layout_options = {
                name: 'cose',
                animate: "end",
                fit: true,
                padding: 10,
                initialTemp: 100,
                animationDuration: 1500,
                nodeOverlap: 6,
                idealEdgeLength: 140,
                nodeDimensionsIncludeLabels: true,
                stop: function() {
                    cy_full.resize();
                }
            },
            layout_options = {
                name: 'cose',
                animationDuration: 1500,
                animate: "end",
                padding: 10,
                nodeOverlap: 6,
                idealEdgeLength: 140,
                nodeDimensionsIncludeLabels: true
            },
            layout = cy_full.layout(layout_options),
            previousTapStamp;

        cy_full.fit();
        layout.run();
        window.cy_full = cy_full;

        cy_full.on('doubleTap', 'node', function(tap_event, event) {
            var tippyA = event.target.data("tippy");
            if (tippyA) {
                tippyA.hide();
                event.target.data("tippy", null);
            }

            event.target.addClass("active");

            if (typeof(event.target.data("expanded")) == "undefined") {
                $.getJSON(event.target.data("details"), function(new_elements) {
                    var root_position = cy_full.$("node[?is_main]").renderedPosition(),
                        pos = event.target.renderedPosition(),
                        misplaced_pos = {
                            x: pos.x + (pos.x - root_position.x) * 0.5,
                            y: pos.y + (pos.y - root_position.y) * 0.5
                        };

                    event.target.data("expanded", true);

                    for (var i = new_elements["nodes"].length - 1; i >= 0; i--) {
                        new_elements["nodes"][i]["data"]["parent_entity"] = event.target.id();
                    }
                    var eles = cy_full.add(new_elements);
                    if (eles.length > 0) {
                        eles.renderedPosition(misplaced_pos);
                        layout.stop();
                        layout = cy_full.layout(partial_layout_options);
                        layout.run();
                    }
                });
            }
        }).on('mouseover', 'node', function(event) {
            var outbound = cy_full.$('edge[source="' + event.target.id() + '"]'),
                inbound = cy_full.$('edge[target="' + event.target.id() + '"]'),
                connections = event.target.data("all_connected"),
                neighbours = [], connections_to_open = 0;
            
            inbound.addClass("active");
            outbound.addClass("active");

            inbound.forEach(function(edge){
                neighbours.push(edge.data("source"));
            });

            outbound.forEach(function(edge){
                neighbours.push(edge.data("target"));
            });

            for (var i = connections.length - 1; i >= 0; i--) {
                if (neighbours.indexOf(connections[i]) == -1) {
                    connections_to_open += 1;
                }
            }


            var tippyA = makeTippy(event.target, connections_to_open);
            tippyA.show();
            event.target.data("tippy", tippyA);
        }).on('mouseout', 'node', function(event) {
            cy_full.$('edge[source="' + event.target.id() + '"], edge[target="' + event.target.id() + '"]').removeClass("active");
            var tippyA = event.target.data("tippy");
            if (tippyA) {
                tippyA.hide();
                event.target.data("tippy", null);
            }
        }).on('mouseover', 'edge', function(event) {
            event.target.addClass("hover");
        }).on('mouseout', 'edge', function(event) {
            event.target.removeClass("hover");
        }).on('tap', function(e) {
            var currentTapStamp = e.timeStamp;
            var msFromLastTap = currentTapStamp - previousTapStamp;

            if (msFromLastTap < 250) {
                e.target.trigger('doubleTap', e);
            }
            previousTapStamp = currentTapStamp;
        });
    }
    $.getJSON($("#profile").data("url"), function(elements) {
        $(".load-pep-modal-tree").on("click", function() {
            var anchor = $(this).data("target");
            $(anchor).modal().on('shown.bs.modal', function(e) {
                init_full(elements);
            });
        }).find("i").removeClass("hidden");
        init_preview(elements);
    });
});
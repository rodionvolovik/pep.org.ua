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

    function init_full(elements) {
        var cy_full = cytoscape({
            container: $('.cy-full'),
            elements: elements,
            layout: {
                name: 'cose',
                animate: "end",
                padding: 10,
                nodeOverlap: 6,
                idealEdgeLength: 140,
                nodeDimensionsIncludeLabels: true,
                randomize: true
            },
            style: full_style
        });

        cy_full.on('click', 'node', function(event) {
            event.target.addClass("active");
        }).on('mouseover', 'node', function(event) {
            cy_full.$('edge[source="' + event.target.id() + '"], edge[target="' + event.target.id() + '"]').addClass("active");
        }).on('mouseout', 'node', function(event) {
            cy_full.$('edge[source="' + event.target.id() + '"], edge[target="' + event.target.id() + '"]').removeClass("active");
        }).on('mouseover', 'edge', function(event) {
            event.target.addClass("hover");
        }).on('mouseout', 'edge', function(event) {
            event.target.removeClass("hover");
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
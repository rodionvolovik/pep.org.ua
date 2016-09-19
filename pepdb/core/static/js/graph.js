$(function() {
    var container = $('#graphme');

    if (container.length > 0) {
        function get_neutral_id(obj) {
            return obj.model + ":" + obj.pk
        }

        function get_color(model, level) {
            var base_color = "#03A9F4";

            switch (model) {
                case "company":
                    base_color = "#FF00FF";
                break;
                case "country":
                    base_color = "#FFFF00";
                break;
            }
            return lighten_hex(base_color, 10 * level);
        }
        
        function get_shape(model, level) {
            var shape;

            switch (model) {
                case "company":
                    shape = "square";
                break;
                case "country":
                    shape = "triangle";
                break;
                default:
                    shape = "dot";
                break;
            }
            return shape;
        }
        function sign(x) {
            if (Math.sign) {
                return Math.sign(x);
            } else if (x === 0) {
                return 0;
            } else {
                return x > 0 ? 1:-1;
            }
        }

        function getCenter() {
            var nodePositions = network.getPositions(),
                keys = Object.keys(nodePositions),
                // Find the sum of all x and y values
                xsum = 0,
                ysum = 0,
                pos,
                i;
    
            for (i = 0; i < keys.length; i++) {
                pos = nodePositions[keys[i]];
                xsum += pos.x;
                ysum += pos.y;
            }

            return [
                xsum / keys.length,
                ysum / keys.length]; // Average is sum divided by length
        }

        function get_spawn_position(parent_id) {
            // Get position of the node with specified id.
            var pos = network.getPositions([parent_id])[parent_id],
                x = pos.x,
                y=pos.y,
                cog = getCenter(),
                dx = cog[0] - x,
                dy = cog[1] - y,
                relSpawnX,
                relSpawnY;

                if (dx === 0) { // Node is directly above center of gravity or on it, so slope will fail.
                    relSpawnX = 0;
                    relSpawnY = -sign(dy) * 100;
                } else {
                    // Compute slope
                    var slope = dy / dx;
                    // Compute the new node position.
                    var dis = 200; // Distance from parent. This should be equal to network.options.physics.springLength;
                    relSpawnX = dis / Math.sqrt(Math.pow(slope, 2) + 1);
                    relSpawnY = relSpawnX * slope;
                }
                return [Math.round(relSpawnX + x), Math.round(relSpawnY + y)];
        }

        function hex_to_rgb(hex) {
            if (hex[0] == "#") {
                hex = hex.slice(1, hex.length);
            }

            strips = [hex.slice(0, 2), hex.slice(2, 4), hex.slice(4, 6)];

            return strips.map(function(x){
                return parseInt(x, 16)
            }); // To RGB
        }

        function rgb_to_hex(rgb) {
            var hexvals = rgb.map(function(x){
                return Math.round(x).toString(16);
            });

            hexvals = hexvals.map(function(x){
                return x.length == 1 ? "0" + x : x;
            });

            return "#" + hexvals.join("");
        }


        function lighten_hex(hex, percent) {
            var rgb = hex_to_rgb(hex); // Convert to RGB
            if (percent > 100) {
                percent = 100; //Limit to 100%
            }

            var new_rgb = rgb.map(function(x) {
                return x + percent / 100.0 * (255 - x);
            });

            return rgb_to_hex(new_rgb); //and back to hex
        }

        function wordwrap(text,limit) {
            var words = text.split(" ");
            var lines = [""];
            for (var i = 0; i < words.length; i++) {
                var word = words[i];
                lastLine = lines[lines.length - 1];

                if (lastLine.length + word.length > limit) {
                    lines.push(word);
                } else {
                    lines[lines.length - 1] = lastLine + " " + word;
                }
            }
            return lines.join("\n").trim();
        }

        function add_node(node, parent) {
            var subnodes = [],
                newedges = [],
                node_id = get_neutral_id(node),
                subnode = nodes.get(node_id),
                node_spawn;

            if (subnode == null) {
                subnode = {
                    id: node_id,
                    label: wordwrap(node.name, 15),
                    title: node.name + "<br/>" + node.description,
                    value: 1,
                    level: 1,
                    color: get_color(node.model, 1),
                    shape: get_shape(node.model, 1),
                    _node: node
                }

                if (typeof(parent) !== "undefined") {
                    subnode.level = parent.level + 1;
                    subnode.parent = parent;
                    subnode.color = get_color(node.model, parent.level + 1);
                    subnode.shape = get_shape(node.model, parent.level + 1);
                    node_spawn = get_spawn_position(parent.id);
                    subnode.x = node_spawn[0];
                    subnode.y = node_spawn[1];
                }

                subnodes.push(subnode);
                nodes.add(subnodes);
            }

            for (var i = 0; i < node.connections.length; i++) {
                var edge = node.connections[i],
                    new_child_node = add_node(
                        edge.node,
                        subnode
                    ),
                    edge_id = get_neutral_id(edge);

                if (edges.getIds().indexOf(edge_id) == -1) {
                    newedges.push({
                        id: edge_id,
                        from: subnode.id,
                        to: new_child_node.id,
                        title: edge.relation,
                        level: subnode.level,
                        selectionWidth: 2,
                        color: "#ccc",
                        hoverWidth: 0
                    });
                }
            }

            edges.add(newedges);
            return subnode;
        }

        function expand_network(url, node) {
            $.get(url, function(data) {
                if (typeof(node) !== "undefined"
                    && data.connections.length > 50) {
                    if (!window.confirm("This will add more than 50 nodes. Are you sure?")) {
                        return;
                    }
                }
                add_node(data, node);
            });
        }

        var options = {
                autoResize: true,
                nodes: {
                    shape: 'dot',
                    scaling: {
                        min: 5,
                        max: 30,
                        label: {
                            min: 3,
                            max: 20,
                            drawThreshold: 10,
                            maxVisible: 15 
                        }
                    },
                    font: {
                        size: 5,
                        face: 'arsenalregular'
                    }
                },
                interaction: {
                    hover: true,
                    hoverConnectedEdges: true,
                    selectConnectedEdges: true,
                },
            },

            nodes = new vis.DataSet(),
            edges = new vis.DataSet(),
            data = {
                nodes: nodes,
                edges: edges
            },
            network = new vis.Network(container.get(0), data, options),
            url = container.data("url");

        network.on("click", function(params) {
            if (params.nodes.length) {
                var clicked_node = nodes.get(params.nodes[0]);
                expand_network(clicked_node._node.details, clicked_node);
            }
        });

        expand_network(url);
        window.network = network;
    }
    
    function modalBodyHeight (modalTarget) {
        var modal = $(modalTarget),
            modalheight = modal.find('.modal-dialog').height(),
            headerheight = modal.find('.modal-header').height(),
            bodyHeight = modalheight - headerheight;
            modal.find('.modal-body').css("height", bodyHeight + "px");
    }
    
    $('#pep-graph-tree').on('shown.bs.modal', function () {
        modalBodyHeight ('#pep-graph-tree');
        $('#graphme').css('height', '100%');
        network.redraw();
        network.fit();
    });
    
    $(window).resize(function() {
        modalBodyHeight ('#pep-graph-tree');
        network.fit();
    });
});

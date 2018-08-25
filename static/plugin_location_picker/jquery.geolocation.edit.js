/**
 * jQuery geolocation.edit plugin
 * Copyright (c) 2012 Milos Popovic <the.elephant@gmail.com>
 * 
 * Freely distributable under the MIT license.
 * 
 * @version 0.0.11 (2014-06-01)
 * @see http://github.com/miloss/jquery-geolocation-edit
 */

(function ($) {
    var inits
      , methods
      , loadScript;
    
    // Queued initializations
    inits = [];
    // Methods container object
    methods = {};
    
    
    // Plugin methods
    // --------------
    
    /**
     * Main execution method
     * @param {Object}  options  Passed plugin options
     */
    methods.main = function (options) {
        var selector = this
          , opts
          , llat, llng, llocation
          , i, addrlen;
          
        // Check for required fields
        if (typeof options.lat === "undefined" ||
                typeof options.lng === "undefined") {
            $.error("Please provide 'lat' and 'lng' options for jQuery.geolocate");
            return;
        }
        
        // If GoogleMaps not loaded - push init to queue and go on
        if (typeof google === "undefined" ||
                typeof google.maps === "undefined") {
            inits.push(function () {
                $(selector).geolocate(options);
            });
            loadScript();
            return;
        }
        
        // Extend default options
        opts = $.extend(true, {
            address: [],
            changeOnEdit: false,
            mapOptions: {
                zoom: 14,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                mapTypeControl: false,
                streetViewControl: false
            },
            markerOptions: {
                draggable:true,
                animation: google.maps.Animation.DROP
            },
            geoCallback: function(){}
        }, options);
        
        $(this).data('opts', opts);
        
        // Init map and marker - per coordinates
        llat = parseFloat( $( opts.lat ).val() );
        llng = parseFloat( $( opts.lng ).val() );
        if (isNaN(llat)) {
            llat = 0;
        }
        if (isNaN(llng)) {
            llng = 0;
        }
        
        llocation = new google.maps.LatLng(llat, llng);
        $(this).geolocate({}, 'initMap', llocation);
        
        // Bind actions - coordinates fields (future?)
        if ( opts.changeOnEdit ) {
            $( opts.lat ).change(function () { /* ... */ });
            $( opts.lng ).change(function () { /* ... */ });
        }
        
        // Bind  actions - address field
        addrlen = opts.address.length;
        if (addrlen > 0) {
            for (i=0; i<addrlen; i++) {
                $( opts.address[i] ).change(function () {
                    $(selector).geolocate({}, 'callGeocoding');
                });
            }
        }
    };
    
    
    /**
     * Initialize GoogleMaps Map on page
     * @param {LatLng} location  GoogleMaps object
     */
    methods.initMap = function (location) {
        var self = $(this).get(0)
          , gmaps = google.maps
          , map
          , markerOptions
          , marker
          , opts = $.data(self, 'opts');
        
        map = new gmaps.Map(self, $.extend({
            center: location
        }, opts.mapOptions));
        
        markerOptions = $.extend({
            map: map,
            position: location
        }, opts.markerOptions);
        
        marker = new gmaps.Marker(markerOptions);
        
        $.data(self, 'map', map);
        $.data(self, 'marker', marker);
        
        gmaps.event.addListener(marker, 'dragend', function () {
            $(self).geolocate({}, 'getMarkerLocation');
        });

        gmaps.event.addListener(map, 'click', function (event) {
            $.data(self, 'marker').setPosition(event.latLng);
            $( opts.lat ).val( event.latLng.lat() );
            $( opts.lng ).val( event.latLng.lng() );
        });
    };
    
    
    /**
     * Make Google Geocoding call with provided address
     */
    methods.callGeocoding = function () {
        var self = $(this).get(0)
          , opts = $.data(self, 'opts')
          , len = opts.address.length
          , cbfunc = opts.geoCallback
          , addr = ''
          , geo;

            
        // Get address
        while (len--) {
            addr += $( opts.address[len] ).val();
        }
        
        // Make request
        geo = new google.maps.Geocoder();
        
        // Geocoder response
        geo.geocode({
            address: addr
        }, function (data, status) {
            var loc, first, map, marker;
            
            cbfunc(data, status);
            
            first = data[0];
            if (typeof first === "undefined") return;
            
            map = $.data(self, "map");
            marker = $.data(self, "marker");
            
            loc = first.geometry.location;
            map.panToBounds( first.geometry.viewport );
            map.panTo( loc );
            marker.setPosition( loc );
            $(self).geolocate({}, "getMarkerLocation");
        });
    };
    
    
    /**
     * Copy marker position to coordinates fields
     */
    methods.getMarkerLocation = function () {
        var self = $(this).get(0)
          , mrk = $.data(self, 'marker')
          , opts = $.data(self, 'opts')
          , pos = mrk.getPosition();
            
        $( opts.lat ).val( pos.lat() );
        $( opts.lng ).val( pos.lng() );
    };
    

    // Plugin function
    // Call appropriate method, or execute "main"
    $.fn.geolocate = function (os, method) {
        var pslice = Array.prototype.slice;
        
        if ( typeof method === 'undefined' ) {
            
            // Only method passed (as 1st parameter)
            if ( typeof os === "string" && typeof methods[os] !== "undefined" ) {
                return methods[ os ].apply( this, pslice.call( arguments, 1 ));
            } else {
                $(this).geolocate({}, 'main', os);
            }
            
        } else if ( methods[method] ) {
            return methods[ method ].apply( this, pslice.call( arguments, 2 ));
            
        } else {
            $.error( "Method " +  method + " does not exist on jQuery.geolocate" );
            
        }
        
        return this;
    };
    
    
    // Callback to GoogleMaps async loading
    // FIXME find non-jQuery.fn-polluting solution
    $.fn.geolocateGMapsLoaded = function () {
        while (inits.length) {
            inits.shift()();
        }
    };
    
    
    // Private functions
    // -----------------
    
    // Load GoogleMaps, we want to do it only once
    // you will need to have a valid API key for google maps and have defined it as the value gmapkey
    // in javasacript for this app this is achieved from private appconfig.ini file by means of
    // populating the constant in the model and then the variable is defined in
    // web2py_ajax.html (maybe not the best place but it works!)

    loadScript = (function(){
        var ran = false;
        
        return function () {
            var script;
            if (ran) return;
            ran = true;
            //console.log(gmapkey);
            script = document.createElement("script");
            script.type = "text/javascript";
            //script.src = "http://maps.googleapis.com/maps/api/js?key=AIzaSyD7_0UmPKGsHjpBln8QdUbbhME-gilX8So&callback=$.fn.geolocateGMapsLoaded";
            script.src = "https://maps.googleapis.com/maps/api/js?key="+gmapkey+"&callback=$.fn.geolocateGMapsLoaded";
            document.body.appendChild(script);
        };
    })();

})(jQuery);

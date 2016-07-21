var Carousel = (function() {
    var Carousel = function(viewerId) {
        var controller = document.createElement("div");

        controller.innerHTML = "TEST";
        controller.style.color = "#ffffff";
        controller.style.paddingLeft = "10px";
        controller.style.position = "relative";
        controller.style.bottom = -this.canvasHeight + "px";
        controller.style.backgroundColor = "rgba(0, 0, 0, 0.7)";

        this.fov = 75;
        this.savedX = 0;
        this.savedY = 0;
        this.longitude = 0;
        this.latitude = 0;
        this.savedLongitude = 0;
        this.savedLatitude = 0;
        this.autoFlow = true;
        this.isUserInteracting = false;
        this.photoWrap = document.getElementById(viewerId);
        this.canvasWidth = this.photoWrap.offsetWidth;
        this.canvasHeight = this.photoWrap.offsetHeight;
    }

    Carousel.prototype = {
        viewer: function(panorama) {
            var sphere = new THREE.SphereGeometry(500, 60, 40);
            sphere.applyMatrix(new THREE.Matrix4().makeScale(-1, 1, 1));

            var sphereMaterial = new THREE.MeshBasicMaterial();
            sphereMaterial.map = new THREE.TextureLoader().load(panorama);

            this.scene = new THREE.Scene();
            this.scene.add(new THREE.Mesh(sphere, sphereMaterial));

            this.camera = new THREE.PerspectiveCamera(this.fov, this.canvasWidth / this.canvasHeight, 1, 1100);
            this.camera.target = new THREE.Vector3(0, 0, 0);

            this.renderer = new THREE.WebGLRenderer();
            this.renderer.setSize(this.canvasWidth, this.canvasHeight);

            this.photoWrap.appendChild(this.renderer.domElement);
            this.photoWrap.addEventListener("mouseup", this.onPhotoMouseUp, false);
            this.photoWrap.addEventListener("mousedown", this.onPhotoMouseDown, false);
            this.photoWrap.addEventListener("mousemove", this.onPhotoMouseMove, false);
            this.photoWrap.addEventListener("mousewheel", this.onPhotoMouseWheel, false );

            this.animate();
        },
        onPhotoMouseUp: function(event) {
            this.isUserInteracting = false;
        },
        onPhotoMouseDown: function(event) {
            event.preventDefault();

            this.autoFlow = false;
            this.isUserInteracting = true;

            this.savedX = event.clientX;
            this.savedY = event.clientY;

            this.savedLongitude = this.longitude;
            this.savedLatitude = this.latitude;
        },
        onPhotoMouseMove: function(event) {
            if (this.isUserInteracting) {
                this.longitude = (this.savedX - event.clientX) * 0.1 + this.savedLongitude;
                this.latitude = (event.clientY - this.savedY) * 0.1 + this.savedLatitude;
            }
        },
        onPhotoMouseWheel: function(event) {
            event.preventDefault();

            if (event.wheelDeltaY) {
                this.fov -= event.wheelDeltaY * 0.05;
            } else if (event.wheelDelta) {
                this.fov -= event.wheelDelta * 0.05;
            } else if (event.detail) {
                this.fov += event.detail * 1.0;
            }

            if (this.fov < 35) {
                this.fov = 35;
            } else if (this.fov > 95) {
                this.fov = 95;
            } else {
                this.fov = 75;
            }

            this.camera.projectionMatrix.makePerspective(this.fov, this.canvasWidth / this.canvasHeight, 1, 1100);

            this.render();
        },
        animate: function() {
            var self = this;

            window.requestAnimationFrame(function() {
                self.animate();
            });
            self.render();
        },
        render: function() {
            if (this.autoFlow) {
                this.longitude += 0.07;
            }

            // limiting latitude from -85 to 85 (cannot point to the sky or under your feet)
            this.latitude = Math.max(-85, Math.min(85, this.latitude));

            // moving the camera according to current latitude (vertical movement) and longitude (horizontal movement)
            this.camera.target.x = 500 * Math.sin(THREE.Math.degToRad(90 - this.latitude)) * Math.cos(THREE.Math.degToRad(this.longitude));
            this.camera.target.y = 500 * Math.cos(THREE.Math.degToRad(90 - this.latitude));
            this.camera.target.z = 500 * Math.sin(THREE.Math.degToRad(90 - this.latitude)) * Math.sin(THREE.Math.degToRad(this.longitude));
            this.camera.lookAt(this.camera.target);

            // calling again render function
            this.renderer.render(this.scene, this.camera);
        }
    };

    return Carousel;
})();

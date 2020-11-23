import os
from .output_field import OutputField
import base64
from skimage.util import img_as_ubyte
from PIL import Image
import io
import numpy as np
import trimesh
import trimesh.exchange.obj
import trimesh.visual
import trimesh.visual.texture


class OutputMeshField(OutputField):
    def __init__(self, field_name, default, rotating=True):
        super(OutputMeshField, self).__init__(field_name, default)
        self.rotating = rotating

    def set_output(self, value):
        assert isinstance(value, dict)
        assert 'vertices' in value
        assert 'faces' in value
        self.value = trimesh.Trimesh(**value)
        # self.value: trimesh.Trimesh = trimesh.load('./mesh.obj')
        if isinstance(self.value.visual, trimesh.visual.texture.TextureVisuals):
            self.value.visual = self.value.visual.to_color()
        center = np.mean(self.value.vertices, axis=0).tolist()
        self.value.vertices = np.array(self.value.vertices) - np.array([center])

    def generate_inputs(self):
        r = np.max(self.value.vertices)

        return """
        <style>
        .canvas_threejs {
             background-color: #FFF;
             width: 512px;
             height: 512px;
             border: 1px solid black;
        }
        </style>""" + f"""
        <div id="{self.field_name}_canvas" class="canvas_threejs"/>
        <script>
        renderer = new THREE.WebGLRenderer();
        var container = document.getElementById('{self.field_name}_canvas');
        var w = container.offsetWidth;
        var h = container.offsetHeight;
        renderer.setSize(w, h);
        container.appendChild(renderer.domElement);
        """ + """
        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera( 75, w/h, 0.1, 1000 );
        
        var directionalLight = new THREE.DirectionalLight( 0xffffff, 0.5 );
        directionalLight.position.set( 1, 1, 0 );
        scene.add( directionalLight );
        var light = new THREE.AmbientLight( 0xffffff );
        scene.add( light );
        
        var loader = new THREE.OBJLoader();
        """ + f"""
        mesh = loader.parse(`{trimesh.exchange.obj.export_obj(self.value)}`); 
        scene.add(mesh);
        mesh.position.set({1.5 * r}, {1.5 * r}, {1.5 * r});
        camera.lookAt( mesh.position );
        """ + """
        
        // controls = new THREE.OrbitControls(camera, renderer.domElement);
        var SPEED = 0.01; 
        function render() {
            requestAnimationFrame( render );
    """ + ("""
            mesh.rotation.x += Math.PI * SPEED / 3.14;
            mesh.rotation.y += Math.PI * Math.PI * SPEED / 3.14 / 3.14;
            mesh.rotation.z += Math.PI * Math.PI * Math.PI * SPEED / 3.14 / 3.14 / 3.14;
    """ if self.rotating else """""") + """
            // controls.update();
            renderer.render( scene, camera );
        }
        render();
        </script>
        """

    @staticmethod
    def make_file_string(value):
        pass

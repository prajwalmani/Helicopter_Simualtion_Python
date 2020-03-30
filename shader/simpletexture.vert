uniform mat4 mvpMatrix;

void main() {
	gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_Position = mvpMatrix * gl_Vertex;
}
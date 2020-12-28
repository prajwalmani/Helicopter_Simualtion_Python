uniform mat4 mvpMatrix;
uniform mat4 mvMatrix;
uniform mat3 normalMatrix;
uniform vec3 lightPosition;

varying vec3 varyingNormal;
varying vec3 varyingLightDir;

void main()
{
	gl_TexCoord[0] = gl_MultiTexCoord0;
	
	varyingNormal = normalMatrix * gl_Normal;
	
	vec4 vPosition4 = mvMatrix * gl_Vertex;
	vec3 vPosition3 = vPosition4.xyz / vPosition4.w;
	
	varyingLightDir = normalize(lightPosition - vPosition3);
	
	gl_Position = mvpMatrix * gl_Vertex;

}

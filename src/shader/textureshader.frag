uniform sampler2D colorMap;

uniform vec4 ambientColor;
uniform vec4 diffuseColor;
uniform vec4 specularColor;
uniform float shininess;
uniform float alpha;
uniform float hasTexture;


varying vec3 varyingNormal;
varying vec3 varyingLightDir;

float intensity(vec3 u, vec3 v)
{
	return max(0.0, dot(normalize(u), normalize(v)));
}

void main()
{
	float diff = intensity(varyingNormal, varyingLightDir);
	vec4 diffCol = diffuseColor;
	if (alpha < 1.0){
		diffCol = vec4(0.5, 0.5, 0.5, 1.0);
	}
	vec4 vFragColor = diffCol + ambientColor;
	if (hasTexture != 0.0)
	{
		vFragColor = texture2D(colorMap, gl_TexCoord[0].st);
	} 
	
	vFragColor.rgb *= clamp(diff, 0.4, 1.2);

	vec3 vReflect = normalize(reflect(-normalize(varyingLightDir), normalize(varyingNormal)));
	float spec = intensity(varyingNormal, vReflect);
	if(diff != 0.0)
	{
		float fSpec = pow(spec, 128.0*shininess);
		vFragColor.rgb += vec3(fSpec, fSpec, fSpec); 
	}
	vFragColor.a = alpha;
	gl_FragColor = clamp(vFragColor, 0.0, 1.0);
}

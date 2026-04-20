import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_padrones.settings')
django.setup()

from usuarios.models import ConfiguracionPortal

texto_md = """Términos y condiciones de uso

Lea atentamente los siguientes Términos y Condiciones de Uso (en adelante e indistintamente Términos) del $URL_PORTAL (en adelante e indistintamente Portal) titularidad de $NOMBRE_ORGANISMO (en adelante e indistintamente $SINONIMO_SITIO, con domicilio en $DIRECCION_ORGANISMO. La utilización del Portal, sus servicios o contenidos implica la aceptación plena y sin reservas de todas las disposiciones contenidas en la versión publicada en el momento en que el usuario acceda al sitio.

En virtud que los Términos pueden ser modificados en cualquier momento por $SINONIMO_SITIO, se recomienda al usuario su atenta lectura en cada una de las ocasiones en que se proponga utilizar el sitio. Las nuevas versiones entrarán en vigor a partir del momento de su publicación en el Portal.

1. Objeto del Portal

El Portal es una herramienta del $NOMBRE_ORGANISMO.

$SINONIMO_SITIO tiene como objetivo facilitar la interacción de forma ágil, de las personas con los contenidos publicados, brindando información detallada y acceso directo a los servicios disponibles en línea.

2. Condición de usuario

Se considera usuario a los efectos de estos Términos cualquier persona física, jurídica o entidad pública, estatal o no, que ingrese al sitio para recorrer, conocer e informarse o utilice el Portal y su contenido, directamente o a través de una aplicación informática.

3. Condiciones de acceso y utilización del Portal

La utilización del Portal tiene carácter gratuito para el usuario, quien se obliga a utilizarlo respetando la normativa nacional vigente, las buenas costumbres y el orden público, comprometiéndose en todos los casos a no causar daños a $NOMBRE_ORGANISMO, a otro usuario o a terceros.

En su mérito, el usuario se abstendrá de utilizar el Portal, sus contenidos o cualquiera de sus servicios con fines o efectos ilícitos, prohibidos en estos Términos, en normas técnicas o jurídicas, lesivos de los derechos e intereses de $NOMBRE_ORGANISMO, de otros usuarios o de terceros, o que de cualquier forma puedan dañar, inutilizar, sobrecargar, deteriorar o impedir la normal utilización del Portal, sus servicios o contenidos, así como de cualquier equipo informático de $NOMBRE_ORGANISMO, de otros usuarios o de terceros.

Salvo indicación en contrario, la información contenida en el Portal será considerada de carácter público. Cuando su uso o tratamiento estén sujetos a algún tipo de restricción deberá estarse a lo indicado expresamente en ese caso.

4. Obligaciones de los usuarios

El usuario se obliga a:

No dañar, inutilizar o deteriorar los sistemas informáticos que sustentan el Portal, los de $NOMBRE_ORGANISMO, de otros usuarios o de terceros, ni los contenidos incorporados y/o almacenados en estos.

No modificar los referidos sistemas de ninguna manera y, consecuentemente, no utilizar versiones de sistemas modificados con el fin de obtener acceso no autorizado a cualquier contenido y/o servicios del sitio.

No interferir ni interrumpir el acceso y utilización del Portal, servidores o redes conectados a este o incumplir los requisitos, procedimientos y regulaciones de la política de conexión de redes.

$NOMBRE_ORGANISMO podrá actuar, por lo medios que considere pertinentes y oportunos, contra cualquier utilización del Portal por usuarios o de terceros que se oponga a estos Términos, infrinja o vulnere derechos de propiedad intelectual , así como cualquier otro derecho de $NOMBRE_ORGANISMO, de otros usuarios o de terceros.

El $NOMBRE_ORGANISMO se reserva la facultad de modificar, en cualquier momento y sin previo aviso, la presentación, configuración, contenidos y servicios del Portal $URL_PORTAL, pudiendo interrumpir, desactivar y/o cancelar cualquiera de los contenidos y/o servicios presentados, integrados o incorporados a este, sin expresión de causa y sin responsabilidad.

5. Propiedad Intelectual

Todas las marcas, nombres comerciales o signos distintivos de cualquier clase que eventualmente aparezcan en este sitio web son propiedad de $NOMBRE_ORGANISMO o de terceros, sin que pueda entenderse que el uso o acceso al sitio atribuye al usuario derecho alguno sobre las citadas marcas, nombres comerciales o signos distintivos de cualquier clase.

6. Responsabilidad del titular del Portal

La veracidad, integridad y actualidad de los contenidos publicados en el Portal son de exclusiva responsabilidad de quien los proporciona.

El $NOMBRE_ORGANISMO se exonera de cualquier responsabilidad por los daños y perjuicios de toda y cualquier naturaleza que puedan deberse a la falta de disponibilidad o continuidad del funcionamiento del Portal, servicios o contenidos, en particular aunque no de modo exclusivo, a su fiabilidad, a los fallos en el acceso a las distintas páginas web o a aquellas desde las que se prestan los servicios o contenidos.

Se procurará anunciar las interrupciones programadas.

7. Enlaces a terceros sitios o portales.

El Portal puede contener dispositivos técnicos de enlace (tales como links, banners, botones) que permiten acceder a sitios web pertenecientes a terceros, con el único objeto de facilitar a los usuarios la búsqueda y acceso a otros sitios y/o contenidos disponibles en Internet.

Los enlaces a otros sitios web, servicios o contenidos, no implican aprobación, en forma alguna, por lo que $NOMBRE_ORGANISMO en su mérito, se deslinda toda responsabilidad contractual, legal o de cualquier otra índole que pudiera derivarse, a modo de ejemplo, por la precisión y uso de los servicios y/o contenidos enlazados.

8. Duración y terminación

El Portal, sus servicios y contenidos tienen una duración indeterminada. Sin perjuicio de ello, podrá ser suspendido temporal o definitivamente, total o parcialmente, por $NOMBRE_ORGANISMO sin expresión de causa y sin responsabilidad, cuando entienda que no están dadas las condiciones para su continuidad.

9. Protección de datos personales

Los datos personales proporcionados en el marco del uso del Portal serán tratados por $NOMBRE_ORGANISMO según lo establecido en la Ley Nº 18.331 del 11 de agosto de 2008 y su decreto reglamentario Nº 414/2009 del 31 de agosto de 2009.

$NOMBRE_ORGANISMO podrá utilizar cookies cuando se utilice el Portal. No obstante, el usuario podrá configurar su navegador para ser avisado de la recepción de las cookies e impedir en caso de considerarlo adecuado, su instalación en el disco duro.

10. Retiro y suspensión de los servicios

$NOMBRE_ORGANISMO podrá retirar o suspender, en cualquier momento y sin necesidad de previo aviso, la prestación de los servicios del Portal a aquellos usuarios que incumplan lo establecido en los presentes Términos.

11. Legislación aplicable y jurisdicción competente

Toda controversia derivada de la aplicación e interpretación de los presentes Términos de Uso, será competencia de los jueces y tribunales ordinarios de la ciudad de Melo, República Oriental del Uruguay.

La ley aplicable será la de la República Oriental del Uruguay.

12. Procedimiento para denunciar contenidos

En caso de contenido erróneo, incompleto, desactualizado, que vulnere derechos de propiedad intelectual o ante cualquier otra situación irregular de hecho o de derecho, el usuario podrá comunicarse a través del correo electrónico: $MAIL_ORGANISMO.

13. Contacto

Por cualquier, queja, sugerencia o propuesta de colaboración, escríbanos a $MAIL_ORGANISMO."""

config, created = ConfiguracionPortal.objects.get_or_create(id=1)
config.texto_terminos_markdown = texto_md
config.save()
print("ConfiguracionPortal poblada exitosamente.")
